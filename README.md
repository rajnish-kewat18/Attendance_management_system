Attendance Management System






🚀 Overview

The Attendance Management System is a secure solution designed to prevent proxy attendance using two-factor authentication. It combines facial recognition with QR code verification, ensuring that attendance is marked only when both checks succeed.

🔑 Features

- Student registration with personal details.

- Capture and store student facial image in the database.

- Generate unique QR code for each student.

Two-step attendance process:

- Facial recognition matches the student’s face with the database.

- QR code is scanned for final verification.

- Attendance is marked only if both verifications succeed.

⚙️ Tech Stack

- Backend: Java Spring Boot / Python

- Database: MySQL / MongoDB

- Libraries: OpenCV, QR Code Generator

📂 Workflow

- Register student details and capture facial image.

- Store data and generate student QR code.

For attendance:

- Face scan → verify with stored image.

- QR scan → verify with stored code.

I- f both steps succeed → attendance marked.

🔮 Future Scope

- Mobile app integration for students and faculty.

- Cloud-based centralized attendance management.
