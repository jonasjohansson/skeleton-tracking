# facecam_transform_cython.pyx
import numpy as np
cimport numpy as cnp
import cv2

def transform_facecam_frame(cnp.ndarray[cnp.uint8_t, ndim=3] frame, 
                           cnp.ndarray[cnp.float32_t, ndim=2] transform_matrix):
    """
    Apply perspective transform to FaceCam frame using Cython for speed.
    """
    cdef int h = frame.shape[0]
    cdef int w = frame.shape[1]
    
    # Apply perspective transform
    transformed = cv2.warpPerspective(frame, transform_matrix, (w, h))
    
    return transformed

def process_facecam_stream(int camera_index, 
                         cnp.ndarray[cnp.float32_t, ndim=2] transform_matrix,
                         str window_name="NDI_FaceCam_Transformed"):
    """
    Process FaceCam stream with Cython optimization.
    """
    cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    
    if not cap.isOpened():
        return False
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Apply transform using Cython function
        transformed = transform_facecam_frame(frame, transform_matrix)
        
        # Display
        cv2.imshow(window_name, transformed)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    return True

