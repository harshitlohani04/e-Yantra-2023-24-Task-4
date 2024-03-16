import cv2
import cv2.aruco as aruco
import pandas as pd
import csv

aruco_data = pd.read_csv('lat_long.csv')

cap = cv2.VideoCapture(0)
# cap = cv2.VideoCapture(0)

# Create an ArUco dictionary
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)

# Create an ArUco parameters object
parameters = aruco.DetectorParameters()

detected_markers = []

# Dictionary with details of aruco marker on robot
robot_marker_id = 80

robot_marker_info = {'id': robot_marker_id, 'lat': None, 'lon': None}


def update_robot_position():
    global robot_marker_info, robot_marker_id, detected_markers

    # Capture a frame from the video feed
    ret, frame = cap.read()
    if not ret:
        print("fuck")
        return

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect ArUco markers
    corners, ids, rejected = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

    # Process detected markers and update robot's position
    if ids is not None:
        detected_markers.clear()
        for marker_id, corner in zip(ids.flatten(), corners):

            if marker_id == robot_marker_id:
                lat = sum(corner[:, 0]) / 4
                lon = sum(corner[:, 1]) / 4
                robot_marker_info['lat'] = lat
                robot_marker_info['lon'] = lon

            # Get marker's information from the CSV file
            csv_marker_info = aruco_data[aruco_data['id'] == marker_id]
            if not csv_marker_info.empty:
                latitude = csv_marker_info['lat'].values[0]
                longitude = csv_marker_info['lon'].values[0]
                detected_markers.append({'id': marker_id, 'lat': latitude, 'lon': longitude})

        # If robot ArUco marker is detected, update QGIS map canvas
        robot_marker_info = get_robot_marker_id()

        if robot_marker_info is not None:
            # Write GPS coordinates to CSV file
            write_gps_to_csv([robot_marker_info])


def write_gps_to_csv(detected_markers):
    # Write GPS coordinates to a CSV file
    csv_filename = "GG_3310_task_4b.csv"

    with open(csv_filename, mode='w', newline='') as csv_file:
        fieldnames = ['id', 'lat', 'lon']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        # Write header
        writer.writeheader()

        # Write data
        for marker in detected_markers:
            writer.writerow(marker)


def calculate_distance(marker, robot_marker):
    # Extracting coordinates
    x1, y1 = marker['lat'], marker['lon']
    x2, y2 = robot_marker['lat'], robot_marker['lon']

    # Euclidean distance calculation
    distance = ((x2 - x1) * 2 + (y2 - y1)*2) * 0.5
    return distance


# Function to get the ID of the robot ArUco marker (assuming the robot has only one marker)
def get_robot_marker_id():
    if not detected_markers:
        return None

    nearest_marker = min(detected_markers, key=lambda marker: calculate_distance(marker, robot_marker_info))

    return nearest_marker


while True:

    update_robot_position()

    if cv2.waitKey(50) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
