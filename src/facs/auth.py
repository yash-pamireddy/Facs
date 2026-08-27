import os
import pickle
import time
import cv2
import face_recognition
import numpy as np

DB_FILE = "users_db.pkl"


def load_database():
  if os.path.exists(DB_FILE):
    with open(DB_FILE, "rb") as f:
      return pickle.load(f)
  return {}


def save_database(db):
  with open(DB_FILE, "wb") as f:
    pickle.dump(db, f)


def capture_multi_angle_face(cap, user_name):
  """Guides the user through capturing multiple head poses for a robust profile."""
  poses = [
      ("CENTER", "Look straight ahead at the camera"),
      ("LEFT", "Turn your head slightly to the LEFT"),
      ("RIGHT", "Turn your head slightly to the RIGHT"),
      ("UP", "Tilt your chin slightly UP"),
  ]

  collected_encodings = []

  print(f"\n--- Starting Multi-Angle Enrollment for {user_name} ---")

  for pose_name, instruction in poses:
    input(f"\n[POSE: {pose_name}] {instruction}. Press ENTER when ready...")
    print(f"Capturing {pose_name}... Hold still!")

    captured = False
    start_time = time.time()

    while time.time() - start_time < 4:
      ret, frame = cap.read()
      if not ret:
        break

      rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
      face_locations = face_recognition.face_locations(rgb_frame)

      cv2.putText(
          frame,
          f"Pose: {pose_name}",
          (30, 50),
          cv2.FONT_HERSHEY_SIMPLEX,
          1,
          (0, 255, 0),
          2,
      )
      cv2.imshow("FACS Multi-Angle Enrollment - Powered by Pulse", frame)
      cv2.waitKey(1)

      if len(face_locations) == 1:
        encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]
        collected_encodings.append(encoding)
        print(f"-> Captured {pose_name} successfully!")
        captured = True
        time.sleep(1)
        break

    if not captured:
      print(f"-> Warning: Could not clearly capture {pose_name}. Moving on.")

  return collected_encodings


def authenticate_or_register():
  db = load_database()
  cap = cv2.VideoCapture(0)

  print("--- FACS Biometric Portal Active ---")
  print("Position your face in front of the camera. Press 's' to scan/login.")

  while True:
    ret, frame = cap.read()
    if not ret:
      break

    cv2.imshow("FACS Portal - Powered by Pulse (Press 's' to Scan)", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
      break

    elif key == ord("s"):
      rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
      face_locations = face_recognition.face_locations(rgb_frame)

      if len(face_locations) == 1:
        unknown_encoding = face_recognition.face_encodings(
            rgb_frame, face_locations
        )[0]

        match_found = False
        matched_name = None

        if db:
          for name, encodings_list in db.items():
            known_encs = np.array(encodings_list)
            matches = face_recognition.compare_faces(
                known_encs, unknown_encoding, tolerance=0.5
            )
            if True in matches:
              match_found = True
              matched_name = name
              break

        if match_found:
          print(
              f"\n[LOGIN SUCCESS] Welcome back, {matched_name}! FACS identity"
              " verified."
          )
          cap.release()
          cv2.destroyAllWindows()
          return matched_name

        print("\n[NEW FACE DETECTED] No matching profile found in Pulse database.")
        cap.release()
        cv2.destroyAllWindows()

        new_name = input("Enter your name to register your FACS ID: ").strip()
        if new_name:
          enroll_cap = cv2.VideoCapture(0)
          multi_encodings = capture_multi_angle_face(enroll_cap, new_name)
          enroll_cap.release()
          cv2.destroyAllWindows()

          if multi_encodings:
            db[new_name] = multi_encodings
            save_database(db)
            print(
                f"\n[REGISTRATION SUCCESS] Multi-angle profile created for"
                f" {new_name} via FACS!"
            )
          else:
            print("Registration failed: No angles were successfully captured.")
        else:
          print("Registration cancelled.")
        return

      elif len(face_locations) > 1:
        print("Multiple faces detected! Please ensure only one person is visible.")
      else:
        print("No face detected clearly. Adjust position and press 's' again.")

  cap.release()
  cv2.destroyAllWindows()


if __name__ == "__main__":
  authenticate_or_register()