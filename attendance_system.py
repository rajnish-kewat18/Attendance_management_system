import mysql.connector
import os
import cv2
import face_recognition
import mysql.connector
import numpy
import qrcode

# Establish a connection to the MySQL database
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root@123",
    database="attendance-management-system"
)

# Create a cursor object
cursor = conn.cursor()

# Path to the folder where student images are stored
image_dir = r"D:\Minor-project\student_image_details"
qr_code_dir = r"D:\Minor-project\qr_code_details"


# Function to register a new student and store their image
def register_student():
    name = input("Enter student name: ")
    age = int(input("Enter student age: "))
    gender = input("Enter student gender: ")
    email = input("Enter student email: ")


    # Register student details in the database
    sql = "INSERT INTO students (name, age, gender, email) VALUES (%s, %s, %s, %s)"
    values = (name, age, gender, email)
    cursor.execute(sql, values)
    conn.commit()
    student_id = cursor.lastrowid  # Get the auto-incremented student ID
    print("Student registered successfully with ID:", student_id)
    generate_qr_code(student_id, name)
    return student_id


# Function to capture and store student image
def capture_image(student_id):
        # Capture the student's image using the webcam
        cam = cv2.VideoCapture(0)
        cv2.namedWindow("Capture Student Image")

        while True:
            ret, frame = cam.read()
            if not ret:
                print("Failed to grab frame")
                break
            cv2.imshow("Capture Student Image", frame)

            k = cv2.waitKey(1)
            if k % 256 == 27:
                # ESC pressed
                print("Escape hit, closing...")
                break
            elif k % 256 == 32:
                # SPACE pressed
                img_name = f"{student_id}.jpg"
                cv2.imwrite(os.path.join(image_dir, img_name), frame)
                print(f"Image captured and saved as {img_name}")
                break

        cam.release()
        cv2.destroyAllWindows()


# Function to generate a QR code
def generate_qr_code(student_id, name):
    qr_data = f"ID: {student_id}, Name: {name}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")
    qr_code_path = os.path.join(qr_code_dir, f"{student_id}.png")
    img.save(qr_code_path)
    print(f"QR code generated and saved as {qr_code_path}")

def generate_qr_codes_for_all_students():
    cursor.execute("SELECT student_id, name FROM students")
    students = cursor.fetchall()
    for student in students:
        student_id, student_name = student
        generate_qr_code(student_id, student_name)



def mark_attendance():
    # Capture a student's image using the webcam
    attendance_img = None
    cam = cv2.VideoCapture(0)
    cv2.namedWindow("Capture Student Image for Attendance")

    while True:
        ret, frame = cam.read()
        if not ret:
            print("Failed to grab frame")
            break
        cv2.imshow("Capture Student Image for Attendance", frame)

        k = cv2.waitKey(1)
        if k % 256 == 32:
            # SPACE pressed
            attendance_img = frame
            break

    cam.release()
    cv2.destroyAllWindows()

    # Check if attendance_img has been assigned
    if attendance_img is None:
        print("No image captured for attendance.")
        return

    # Load stored images and compare faces
    known_face_encodings = []
    known_student_ids = []

    for file in os.listdir(image_dir):
        img_path = os.path.join(image_dir, file)
        img = cv2.imread(img_path)
        face_encodings = face_recognition.face_encodings(img)

        if face_encodings:
            known_face_encodings.append(face_encodings[0])
            student_id = os.path.splitext(file)[0]
            known_student_ids.append(student_id)

    # Detect face locations and encodings in the captured image
    face_locations = face_recognition.face_locations(attendance_img)
    face_encodings = face_recognition.face_encodings(attendance_img, face_locations)

    if not face_encodings:
        print("No faces detected in the captured image.")
        return

    # Compare faces and mark attendance only if the face matches
    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = numpy.argmin(face_distances)

        if matches[best_match_index]:
            student_id = known_student_ids[best_match_index]
            break
    else:
        print("Face not recognized")
        return

    # Scan QR code using the webcam to verify the same student
    # cam = cv2.VideoCapture(0)
    cap = cv2.VideoCapture(0)
    qr_detector = cv2.QRCodeDetector()

    scanned_qr = None  # Variable to store the last scanned QR code

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        qr_data, bbox, _ = qr_detector.detectAndDecode(frame)

        if qr_data and qr_data != scanned_qr:
            print("QR Code Data:", qr_data)
            scanned_qr = qr_data  # Store the scanned QR data

            # Extract student_id and student_name from QR data
            qr_data_split = qr_data.split(", ")
            if len(qr_data_split) == 2 and qr_data_split[0].startswith("ID: ") and qr_data_split[1].startswith(
                    "Name: "):
                student_id = qr_data_split[0].replace("ID: ", "")
                student_name = qr_data_split[1].replace("Name: ", "")

                try:
                    # Update attendance in the database
                    sql = "INSERT INTO attendance (student_id, date, in_time) VALUES (%s, CURDATE(), CURTIME())"
                    values = (student_id,)
                    cursor.execute(sql, values)
                    conn.commit()
                    print(f"Attendance marked for student {student_name} with ID {student_id}")
                except mysql.connector.Error as err:
                    print(f"Error while updating attendance table: {err}")

        if bbox is not None and qr_data:
            cv2.putText(frame, qr_data, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("QR Code Scanner", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


# Main menu
def main_menu():
    while True:
        print("\n1. Register Student and capture image ")
        print("2. Take Attendance")
        print("3. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            student_id = register_student()
            capture_image(student_id)
            generate_qr_codes_for_all_students()


        elif choice == '2':
            mark_attendance()
        elif choice == '3':
            break
        else:
            print("Invalid choice, please try again.")


# Run the main menu
main_menu()

# Close the database connection
cursor.close()
conn.close()




