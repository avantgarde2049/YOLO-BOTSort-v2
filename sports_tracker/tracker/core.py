import os
import cv2
import time
from datetime import datetime


class SportsTracker:
    def __init__(self, debug=False):
        self.debug = debug
        self.processor = None
        self.processing_times = []

    def process_video(self, input_path, output_path, max_frames=None):
        """Process video with comprehensive error checking"""
        try:
            # Validate input file
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"Input file not found: {input_path}")

            # Initialize processor if not already done
            if not self.processor:
                from main import SportsVideoProcessor
                self.processor = SportsVideoProcessor()

            # Process the video
            start_time = time.time()
            success = self._safe_process(input_path, output_path)
            processing_time = time.time() - start_time

            if self.debug:
                print(f"Processing completed in {processing_time:.2f} seconds")
                print(f"Input: {input_path}")
                print(f"Output: {output_path}")

            return success, "Video processed successfully"

        except Exception as e:
            if self.debug:
                print(f"Processing failed: {str(e)}")
            return False, str(e)

    def _safe_process(self, input_path, output_path):
        """Process video with frame-by-frame validation"""
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            raise ValueError("Could not open video file")

        try:
            # Get video properties
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)

            # Initialize video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

            frame_count = 0
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                try:
                    # Process frame
                    vis_frame, _, _ = self.processor.process_frame(frame, frame_count)
                    if vis_frame is not None:
                        out.write(vis_frame)
                    frame_count += 1
                except Exception as e:
                    if self.debug:
                        print(f"Frame {frame_count} error: {str(e)}")
                    continue

            return frame_count > 0  # Success if at least one frame processed

        finally:
            cap.release()
            if 'out' in locals():
                out.release()

    def generate_frames(self, video_path):
        """Generate frames for streaming"""
        cap = cv2.VideoCapture(video_path)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            try:
                # Process frame
                vis_frame, _, _ = self.processor.process_frame(frame, 0)
                ret, buffer = cv2.imencode('.jpg', vis_frame)
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            except Exception as e:
                if self.debug:
                    print(f"Streaming error: {str(e)}")
                continue

        cap.release()

    def get_performance_stats(self):
        """Get processing statistics"""
        if not self.processor:
            return {}

        return {
            'processing_fps': self._calculate_fps(),
            'active_tracks': len(self.processor.tracks),
            'frame_count': getattr(self.processor, 'frame_count', 0),
            'timestamp': datetime.now().isoformat()
        }

    def _calculate_fps(self):
        if len(self.processing_times) < 2:
            return 0
        return len(self.processing_times) / sum(self.processing_times)