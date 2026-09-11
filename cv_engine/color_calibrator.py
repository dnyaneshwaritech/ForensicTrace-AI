import cv2
import numpy as np

def rgb_to_lab(rgb_color):
    """
    Converts an (R, G, B) tuple [0-255] to CIELAB space (L*, a*, b*).
    """
    # Create 1x1 BGR image for OpenCV conversion
    r, g, b = rgb_color
    bgr = np.uint8([[[b, g, r]]])
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)[0][0]
    
    # Scale OpenCV LAB to standard ranges: L: 0-100, a: -128..127, b: -128..127
    L = lab[0] * (100.0 / 255.0)
    a = lab[1] - 128.0
    b_val = lab[2] - 128.0
    return L, a, b_val


def ciede2000(lab1, lab2):
    """
    Calculates the CIEDE2000 (Delta E 00) color difference between two LAB colors.
    """
    L1, a1, b1 = lab1
    L2, a2, b2 = lab2

    avg_L = (L1 + L2) / 2.0
    C1 = np.sqrt(a1**2 + b1**2)
    C2 = np.sqrt(a2**2 + b2**2)
    avg_C = (C1 + C2) / 2.0

    G = 0.5 * (1 - np.sqrt((avg_C**7) / (avg_C**7 + 25**7 + 1e-8)))
    a1_p = (1 + G) * a1
    a2_p = (1 + G) * a2

    C1_p = np.sqrt(a1_p**2 + b1**2)
    C2_p = np.sqrt(a2_p**2 + b2**2)
    avg_C_p = (C1_p + C2_p) / 2.0

    h1_p = np.degrees(np.arctan2(b1, a1_p)) % 360
    h2_p = np.degrees(np.arctan2(b2, a2_p)) % 360

    if abs(h1_p - h2_p) > 180:
        avg_H_p = (h1_p + h2_p + 360) / 2.0
    else:
        avg_H_p = (h1_p + h2_p) / 2.0

    T = (1 - 0.17 * np.cos(np.radians(avg_H_p - 30)) +
         0.24 * np.cos(np.radians(2 * avg_H_p)) +
         0.32 * np.cos(np.radians(3 * avg_H_p + 6)) -
         0.20 * np.cos(np.radians(4 * avg_H_p - 63)))

    if abs(h1_p - h2_p) <= 180:
        dh_p = h2_p - h1_p
    elif h2_p <= h1_p:
        dh_p = h2_p - h1_p + 360
    else:
        dh_p = h2_p - h1_p - 360

    dH_p = 2 * np.sqrt(C1_p * C2_p) * np.sin(np.radians(dh_p / 2.0))

    dL_p = L2 - L1
    dC_p = C2_p - C1_p

    S_L = 1 + (0.015 * (avg_L - 50)**2) / np.sqrt(20 + (avg_L - 50)**2)
    S_C = 1 + 0.045 * avg_C_p
    S_H = 1 + 0.015 * avg_C_p * T

    dTh = 30 * np.exp(-(((avg_H_p - 275) / 25)**2))
    R_C = 2 * np.sqrt((avg_C_p**7) / (avg_C_p**7 + 25**7 + 1e-8))
    R_T = -np.sin(np.radians(2 * dTh)) * R_C

    delta_E = np.sqrt(
        (dL_p / S_L)**2 +
        (dC_p / S_C)**2 +
        (dH_p / S_H)**2 +
        R_T * (dC_p / S_C) * (dH_p / S_H)
    )
    return delta_E


class ColorCalibrator:
    """
    Normalizes image colors using standard white balance or reference color cards.
    """

    @staticmethod
    def extract_dominant_rgb(image_patch):
        """
        Extracts median RGB color from an image region (patch) to remove noise.
        """
        if image_patch is None or image_patch.size == 0:
            return (0, 0, 0)
        
        # Convert BGR (OpenCV format) to RGB
        rgb_patch = cv2.cvtColor(image_patch, cv2.COLOR_BGR2RGB)
        median_r = int(np.median(rgb_patch[:, :, 0]))
        median_g = int(np.median(rgb_patch[:, :, 1]))
        median_b = int(np.median(rgb_patch[:, :, 2]))
        return (median_r, median_g, median_b)

    @staticmethod
    def apply_gray_world_white_balance(image):
        """
        Applies Gray-World White Balance algorithm to compensate for ambient lighting.
        """
        b, g, r = cv2.split(image)
        mean_b, mean_g, mean_r = np.mean(b), np.mean(g), np.mean(r)

        # Target gray value
        gray_val = (mean_b + mean_g + mean_r) / 3.0

        kb = gray_val / (mean_b + 1e-5)
        kg = gray_val / (mean_g + 1e-5)
        kr = gray_val / (mean_r + 1e-5)

        b_balanced = np.clip(b * kb, 0, 255).astype(np.uint8)
        g_balanced = np.clip(g * kg, 0, 255).astype(np.uint8)
        r_balanced = np.clip(r * kr, 0, 255).astype(np.uint8)

        return cv2.merge([b_balanced, g_balanced, r_balanced])
