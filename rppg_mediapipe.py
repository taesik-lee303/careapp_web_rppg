"""
rPPG (remote Photoplethysmography) 측정 모듈 (MediaPipe 버전)
웹캠을 통해 얼굴의 색상 변화를 감지하여 심박수를 측정합니다.
MediaPipe를 사용하여 dlib 없이도 작동합니다.
"""

import cv2
import numpy as np
from scipy import signal
from scipy.fft import fft, fftfreq
import mediapipe as mp
from collections import deque
import time


class RPPGDetector:
    def __init__(self, buffer_size=300, fps=30):
        """
        rPPG 감지기 초기화
        
        Args:
            buffer_size: 신호 버퍼 크기 (프레임 수)
            fps: 초당 프레임 수
        """
        self.buffer_size = buffer_size
        self.fps = fps
        
        # MediaPipe 얼굴 감지 초기화
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=1, min_detection_confidence=0.5
        )
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # 신호 버퍼
        self.signal_buffer = deque(maxlen=buffer_size)
        self.timestamp_buffer = deque(maxlen=buffer_size)
        
        # ROI 영역 (이마 부분)
        self.roi_points = None
        
    def get_forehead_roi(self, face_landmarks, image_width, image_height):
        """
        얼굴 랜드마크에서 이마 영역(ROI) 추출
        
        Args:
            face_landmarks: MediaPipe 얼굴 랜드마크
            image_width: 이미지 너비
            image_height: 이미지 높이
            
        Returns:
            ROI 포인트 리스트
        """
        if face_landmarks is None:
            return None
        
        # MediaPipe 랜드마크 인덱스
        # 이마 영역: 10, 151, 337, 9, 107, 55, 65, 52, 53, 46, 124, 35
        forehead_indices = [10, 151, 337, 9, 107, 55, 65, 52, 53, 46, 124, 35]
        
        points = []
        for idx in forehead_indices:
            landmark = face_landmarks.landmark[idx]
            x = int(landmark.x * image_width)
            y = int(landmark.y * image_height)
            points.append([x, y])
        
        return np.array(points, dtype=np.int32)
    
    def extract_roi_signal(self, frame, roi_points):
        """
        ROI 영역에서 색상 신호 추출
        
        Args:
            frame: 비디오 프레임
            roi_points: ROI 포인트
            
        Returns:
            평균 녹색 채널 값
        """
        if roi_points is None or len(roi_points) < 3:
            return None
        
        # ROI 마스크 생성
        mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        cv2.fillPoly(mask, [roi_points], 255)
        
        # ROI 영역에서 평균 색상 추출 (녹색 채널이 가장 민감함)
        roi_region = cv2.bitwise_and(frame, frame, mask=mask)
        green_channel = roi_region[:, :, 1]  # BGR에서 녹색 채널
        
        # 마스크된 영역의 평균값 계산
        masked_green = green_channel[mask > 0]
        if len(masked_green) > 0:
            return np.mean(masked_green)
        
        return None
    
    def process_frame(self, frame):
        """
        프레임 처리 및 신호 추출
        
        Args:
            frame: 비디오 프레임
            
        Returns:
            처리된 프레임, ROI 포인트, 현재 신호 값
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 얼굴 감지
        face_results = self.face_detection.process(rgb_frame)
        
        if face_results.detections is None or len(face_results.detections) == 0:
            return frame, None, None
        
        # 얼굴 메시 감지
        mesh_results = self.face_mesh.process(rgb_frame)
        
        if mesh_results.multi_face_landmarks is None or len(mesh_results.multi_face_landmarks) == 0:
            # 메시가 없으면 얼굴 감지 결과로 ROI 추정
            detection = face_results.detections[0]
            bbox = detection.location_data.relative_bounding_box
            h, w = frame.shape[:2]
            
            x = int(bbox.xmin * w)
            y = int(bbox.ymin * h)
            width = int(bbox.width * w)
            height = int(bbox.height * h)
            
            # 이마 영역 추정
            roi_points = np.array([
                [x + width//4, y + height//10],
                [x + 3*width//4, y + height//10],
                [x + 3*width//4, y + height//3],
                [x + width//4, y + height//3]
            ], dtype=np.int32)
        else:
            # 얼굴 메시에서 ROI 추출
            face_landmarks = mesh_results.multi_face_landmarks[0]
            h, w = frame.shape[:2]
            roi_points = self.get_forehead_roi(face_landmarks, w, h)
        
        # 신호 추출
        signal_value = self.extract_roi_signal(frame, roi_points)
        
        # ROI 그리기
        if roi_points is not None:
            cv2.polylines(frame, [roi_points], True, (0, 255, 0), 2)
        
        return frame, roi_points, signal_value
    
    def add_signal(self, signal_value):
        """
        신호 버퍼에 값 추가
        
        Args:
            signal_value: 신호 값
        """
        if signal_value is not None:
            self.signal_buffer.append(signal_value)
            self.timestamp_buffer.append(time.time())
    
    def calculate_heart_rate(self, min_bpm=40, max_bpm=200):
        """
        수집된 신호로부터 심박수 계산
        
        Args:
            min_bpm: 최소 심박수
            max_bpm: 최대 심박수
            
        Returns:
            계산된 심박수 (BPM), 신뢰도 점수
        """
        if len(self.signal_buffer) < 60:  # 최소 2초 데이터 필요
            return None, 0.0
        
        # 신호를 numpy 배열로 변환
        signal_array = np.array(self.signal_buffer)
        
        # 신호 정규화 및 디트렌딩
        signal_array = signal_array - np.mean(signal_array)
        
        # 밴드패스 필터 적용 (0.7-4 Hz, 심박수 범위)
        nyquist = self.fps / 2
        low = 0.7 / nyquist
        high = 4.0 / nyquist
        b, a = signal.butter(3, [low, high], btype='band')
        filtered_signal = signal.filtfilt(b, a, signal_array)
        
        # FFT를 통한 주파수 분석
        fft_values = fft(filtered_signal)
        fft_freq = fftfreq(len(filtered_signal), 1.0 / self.fps)
        
        # 심박수 범위에 해당하는 주파수만 고려
        min_freq = min_bpm / 60.0
        max_freq = max_bpm / 60.0
        
        # 해당 범위의 인덱스 찾기
        freq_mask = (fft_freq >= min_freq) & (fft_freq <= max_freq)
        
        if not np.any(freq_mask):
            return None, 0.0
        
        # 주파수 범위 내에서 최대 파워를 가진 주파수 찾기
        power_spectrum = np.abs(fft_values)
        power_spectrum[~freq_mask] = 0
        
        max_power_idx = np.argmax(power_spectrum)
        dominant_freq = abs(fft_freq[max_power_idx])
        
        # BPM으로 변환
        heart_rate = dominant_freq * 60
        
        # 신뢰도 계산 (개선된 방식)
        max_power = power_spectrum[max_power_idx]
        
        # 피크 주변의 파워 제외하고 평균 계산 (노이즈 추정)
        # 피크 주변 ±2개 인덱스 제외
        peak_window = 2
        noise_mask = freq_mask.copy()
        if max_power_idx - peak_window >= 0 and max_power_idx + peak_window < len(noise_mask):
            noise_mask[max(0, max_power_idx - peak_window):min(len(noise_mask), max_power_idx + peak_window + 1)] = False
        
        if np.any(noise_mask):
            noise_power = np.mean(power_spectrum[noise_mask])
        else:
            # 피크 주변만 있으면 전체 평균 사용
            noise_power = np.mean(power_spectrum[freq_mask])
        
        # Signal-to-Noise Ratio (SNR) 기반 신뢰도
        snr = max_power / (noise_power + 1e-6)
        
        # SNR을 0-1 범위로 정규화 (경험적 임계값 사용)
        # SNR이 2 이상이면 높은 신뢰도, 1 이하면 낮은 신뢰도
        snr_threshold_low = 1.0
        snr_threshold_high = 5.0
        confidence = np.clip((snr - snr_threshold_low) / (snr_threshold_high - snr_threshold_low), 0.0, 1.0)
        
        # 추가: 피크의 두드러짐 (peak prominence) 고려
        # 최대값이 두 번째 최대값보다 얼마나 큰지
        sorted_powers = np.sort(power_spectrum[freq_mask])[::-1]
        if len(sorted_powers) > 1:
            peak_prominence = (max_power - sorted_powers[1]) / (max_power + 1e-6)
            # prominence를 신뢰도에 반영 (가중 평균)
            confidence = 0.7 * confidence + 0.3 * peak_prominence
        
        return heart_rate, confidence
    
    def calculate_respiration_rate(self, min_rpm=8, max_rpm=30):
        """
        수집된 신호로부터 호흡률 계산
        
        Args:
            min_rpm: 최소 호흡률 (분당 호흡 수)
            max_rpm: 최대 호흡률 (분당 호흡 수)
            
        Returns:
            계산된 호흡률 (RPM), 신뢰도 점수
        """
        if len(self.signal_buffer) < 180:  # 최소 6초 데이터 필요 (호흡률은 더 긴 시간 필요)
            return None, 0.0
        
        # 신호를 numpy 배열로 변환
        signal_array = np.array(self.signal_buffer)
        
        # 신호 정규화 및 디트렌딩
        signal_array = signal_array - np.mean(signal_array)
        
        # 밴드패스 필터 적용 (0.1-0.5 Hz, 호흡률 범위)
        nyquist = self.fps / 2
        low = 0.1 / nyquist
        high = 0.5 / nyquist
        b, a = signal.butter(3, [low, high], btype='band')
        filtered_signal = signal.filtfilt(b, a, signal_array)
        
        # FFT를 통한 주파수 분석
        fft_values = fft(filtered_signal)
        fft_freq = fftfreq(len(filtered_signal), 1.0 / self.fps)
        
        # 호흡률 범위에 해당하는 주파수만 고려
        min_freq = min_rpm / 60.0
        max_freq = max_rpm / 60.0
        
        # 해당 범위의 인덱스 찾기
        freq_mask = (fft_freq >= min_freq) & (fft_freq <= max_freq)
        
        if not np.any(freq_mask):
            return None, 0.0
        
        # 주파수 범위 내에서 최대 파워를 가진 주파수 찾기
        power_spectrum = np.abs(fft_values)
        power_spectrum[~freq_mask] = 0
        
        max_power_idx = np.argmax(power_spectrum)
        dominant_freq = abs(fft_freq[max_power_idx])
        
        # RPM으로 변환
        respiration_rate = dominant_freq * 60
        
        # 신뢰도 계산 (개선된 방식)
        max_power = power_spectrum[max_power_idx]
        
        # 피크 주변의 파워 제외하고 평균 계산 (노이즈 추정)
        # 피크 주변 ±2개 인덱스 제외
        peak_window = 2
        noise_mask = freq_mask.copy()
        if max_power_idx - peak_window >= 0 and max_power_idx + peak_window < len(noise_mask):
            noise_mask[max(0, max_power_idx - peak_window):min(len(noise_mask), max_power_idx + peak_window + 1)] = False
        
        if np.any(noise_mask):
            noise_power = np.mean(power_spectrum[noise_mask])
        else:
            # 피크 주변만 있으면 전체 평균 사용
            noise_power = np.mean(power_spectrum[freq_mask])
        
        # Signal-to-Noise Ratio (SNR) 기반 신뢰도
        snr = max_power / (noise_power + 1e-6)
        
        # SNR을 0-1 범위로 정규화 (경험적 임계값 사용)
        # 호흡률은 더 낮은 주파수이므로 임계값 조정
        snr_threshold_low = 0.8
        snr_threshold_high = 4.0
        confidence = np.clip((snr - snr_threshold_low) / (snr_threshold_high - snr_threshold_low), 0.0, 1.0)
        
        # 추가: 피크의 두드러짐 (peak prominence) 고려
        sorted_powers = np.sort(power_spectrum[freq_mask])[::-1]
        if len(sorted_powers) > 1:
            peak_prominence = (max_power - sorted_powers[1]) / (max_power + 1e-6)
            # prominence를 신뢰도에 반영 (가중 평균)
            confidence = 0.7 * confidence + 0.3 * peak_prominence
        
        return respiration_rate, confidence
    
    def get_signal_stats(self):
        """
        현재 신호 통계 반환
        
        Returns:
            버퍼 크기, 평균 신호 값
        """
        if len(self.signal_buffer) == 0:
            return 0, 0
        
        return len(self.signal_buffer), np.mean(self.signal_buffer)

