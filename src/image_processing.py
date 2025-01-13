import cv2
import numpy as np

class ImageProcessor:
    @staticmethod
    def enhance_image(image, for_symbols=False):
        """
        Enhance image for better OCR
        Args:
            image: Input image
            for_symbols: Boolean to indicate if enhancement is for technical symbols
        """
        image_np = np.array(image)
        gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
        
        if for_symbols:
            # Enhanced preprocessing for technical symbols
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
            contrasted = clahe.apply(gray)
            denoised = cv2.fastNlMeansDenoising(contrasted)
            binary = cv2.adaptiveThreshold(
                denoised,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                11,
                2
            )
            kernel = np.ones((2,2), np.uint8)
            return cv2.dilate(binary, kernel, iterations=1)
        else:
            # Standard enhancement
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(gray)
            _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            return binary