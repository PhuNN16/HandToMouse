import cv2 as cv
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.framework.formats import landmark_pb2
import time
from cursor_control import move_mouse

# Needs to be global for it to store properly
# This is because the print_result callback function is running async
latest_result : list = None

# Initial x y value will need to be replaced when previous_xy is none
previous_xy : tuple = None

# Attempt to reduce the effect the shakiness of the model has on the cursor
def modify_vector_movement(vec: tuple):
    x, y = vec[0], vec[1]
    if abs(x) < 0.003:
        x = 0
    if abs(y) < 0.003:
        y = 0
    return (x*100, y*100)


def convert_landmarks_to_pb(landmark_list):
    # Convert the MediaPipe task landmarks to core framework landmarks
    converted_landmarks = []
    for landmark in landmark_list:
        # Create a new NormalizedLandmark from the task's NormalizedLandmark
        pb_landmark = landmark_pb2.NormalizedLandmark(
            x=landmark.x,
            y=landmark.y,
            z=landmark.z
        )
        converted_landmarks.append(pb_landmark)
    
    # Return the NormalizedLandmarkList
    return landmark_pb2.NormalizedLandmarkList(landmark=converted_landmarks)


def main():
    # Camera set up
    capture : cv.VideoCapture = cv.VideoCapture(0)
    capture.set(cv.CAP_PROP_FRAME_HEIGHT, 2000)
    capture.set(cv.CAP_PROP_FRAME_WIDTH, 2000)

    # Loading mediapipe hand landmarks
    mp_hand_model_path : str = "model/hand_landmarker.task"

    BaseOptions = mp.tasks.BaseOptions
    HandLandmarker = mp.tasks.vision.HandLandmarker
    HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
    HandLandmarkerResult = mp.tasks.vision.HandLandmarkerResult
    VisionRunningMode = mp.tasks.vision.RunningMode


    # Initialize MediaPipe drawing utilities
    mp_drawing = mp.solutions.drawing_utils
    mp_hands_connections = mp.solutions.hands.HAND_CONNECTIONS


    # Create a hand landmarker instance with the live stream mode:
    def print_result(result: HandLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
        # global keyword is needed because print result callback function runs async and would just be None without it
        global latest_result
        if result.hand_landmarks:  # Ensure landmarks are detected
            latest_result = result  # Store latest result
        else:
            latest_result = None  # Reset if no hand is detected

    options = HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=mp_hand_model_path),
        running_mode=VisionRunningMode.LIVE_STREAM,
        result_callback=print_result,
        num_hands=1
    )

    with HandLandmarker.create_from_options(options) as landmarker:
        while True:
            isTrue, frame = capture.read()
            if not isTrue:
                print("failed to grab frames")
                break

            frame = cv.flip(frame, 1) # 0 is z axis, 1 is y, -1 is x
            # frame = cv.resize(frame, (750, 750), interpolation=cv.INTER_AREA)

            timestamp = int(time.time() * 1000)  # Convert milliseconds to microseconds
            # print(f"Frame Timestamp: {timestamp} µs")


            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)

            landmarker.detect_async(mp_image, timestamp)
            
            # print(latest_result)
            
            # Draw landmarks if available

            # Draw landmarks if available
            
            if latest_result and latest_result.hand_landmarks:
                # # This is to draw the landmarks onto the video feedback
                # for hand_landmarks in latest_result.hand_landmarks:
                #     # Convert list of landmarks into a format draw_landmarks can process
                #     # landmark_list = mp.solutions.hands.HandLandmark  # Correct structure
                #     # draw_landmarks() needs a NormalizedLandmarkList object
                #     pb2_landmark_list = convert_landmarks_to_pb(hand_landmarks)
                #     # print(pb2_landmark_list)
                #     mp_drawing.draw_landmarks(
                #         frame,  # OpenCV frame
                #         pb2_landmark_list,  # Corrected: Now directly passing the object
                #         mp_hands_connections,
                #         mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=3),  # Landmark style
                #         mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)  # Connection style
                #     )

                current_res: landmark_pb2.NormalizedLandmark = latest_result.hand_landmarks[0][8]

                # Needs to be a global variable to change properly
                global previous_xy
                if previous_xy == None:
                    previous_xy = (current_res.x, current_res.y)
                else:
                    # TODO: Print out current_res - previous_xy, try to see if we can discretized the values
                    # This will make it more stable
                    vector_movement = (
                        current_res.x - previous_xy[0],
                        current_res.y - previous_xy[1]
                    )
                    print(modify_vector_movement(vector_movement))
                    
                    move_mouse(modify_vector_movement(vector_movement), 25)

                    previous_xy = (current_res.x, current_res.y)
            else:
                # This is put here in case your hand leaves the screen, when it comes back the vector_movement won't be insanely large
                previous_xy = None
            
            # play video for debugging purposes
            # cv.imshow("Video", frame)

            # if cv.waitKey(10) & 0xFF == ord('d'):
            #     break

        
    capture.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    main()