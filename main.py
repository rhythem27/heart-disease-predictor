import customtkinter as ctk
from tkinter import messagebox
import sqlite3
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
import bcrypt

DB_FILE = "enhanced_database.db"
DATASET_FILE = "heart_failure_clinical_records_dataset.csv"

# Set the customtkinter appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


def setup_database():
    """Initializes the SQLite database."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT UNIQUE NOT NULL,
                            password TEXT NOT NULL,
                            role TEXT NOT NULL)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS logs (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            doctor_id INTEGER NOT NULL,
                            age REAL, anaemia INTEGER, creatinine_phosphokinase INTEGER,
                            diabetes INTEGER, ejection_fraction INTEGER,
                            high_blood_pressure INTEGER, platelets REAL,
                            serum_creatinine REAL, serum_sodium INTEGER,
                            sex INTEGER, smoking INTEGER, time INTEGER,
                            risk_prediction INTEGER, risk_probability REAL,
                            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (doctor_id) REFERENCES users (id))''')
        # Insert default admin
        hashed_password = bcrypt.hashpw(b"adminpass", bcrypt.gensalt())
        cursor.execute('''INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)''',
                       ("admin", hashed_password, "admin"))
        conn.commit()


class PatientRiskPredictor:
    def __init__(self, dataset_path):
        self.scaler = StandardScaler()
        self.model = None
        self.train_model(dataset_path)

    def train_model(self, dataset_path):
        """Train the RandomForest model using the dataset."""
        data = pd.read_csv(dataset_path)
        X = data.drop(columns=["DEATH_EVENT"])
        y = data["DEATH_EVENT"]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Scale and balance the dataset
        X_train_scaled = self.scaler.fit_transform(X_train)
        smote = SMOTE(random_state=42)
        X_train_balanced, y_train_balanced = smote.fit_resample(X_train_scaled, y_train)

        # Train the RandomForestClassifier
        self.model = RandomForestClassifier(random_state=42)
        self.model.fit(X_train_balanced, y_train_balanced)

    def predict(self, features):
        """Predicts patient risk based on input features."""
        try:
            features_scaled = self.scaler.transform([features])
            prediction = self.model.predict(features_scaled)[0]
            probability = self.model.predict_proba(features_scaled)[0][1]
            return prediction, probability
        except Exception as e:
            raise ValueError(f"Model prediction failed: {e}")


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Patient Risk Prediction")
        self.root.geometry("700x600")
        self.db = sqlite3.connect(DB_FILE)
        self.create_login_screen()

    def create_login_screen(self):
        """Creates the login screen."""
        self.clear_screen()

        ctk.CTkLabel(self.root, text="Login", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        ctk.CTkLabel(self.root, text="Username").pack()
        self.username_entry = ctk.CTkEntry(self.root)
        self.username_entry.pack(pady=10)
        ctk.CTkLabel(self.root, text="Password").pack()
        self.password_entry = ctk.CTkEntry(self.root, show="*")
        self.password_entry.pack(pady=10)
        ctk.CTkButton(self.root, text="Login", command=self.handle_login).pack(pady=20)

    def handle_login(self):
        """Handles user login."""
        username = self.username_entry.get()
        password = self.password_entry.get()
        cursor = self.db.cursor()
        cursor.execute("SELECT id, password, role FROM users WHERE username=?", (username,))
        result = cursor.fetchone()

        if result:
            user_id, hashed_password, role = result
            if bcrypt.checkpw(password.encode(), hashed_password):
                if role == "admin":
                    self.create_admin_screen()
                elif role == "doctor":
                    self.create_doctor_screen(user_id)
            else:
                messagebox.showerror("Error", "Invalid password")
        else:
            messagebox.showerror("Error", "User does not exist")

    def create_admin_screen(self):
        """Creates the admin portal."""
        self.clear_screen()
        ctk.CTkLabel(self.root, text="Admin Portal", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        ctk.CTkButton(self.root, text="View Logs", command=self.view_logs).pack(pady=10)
        ctk.CTkButton(self.root, text="Add Doctor", command=self.add_doctor).pack(pady=10)
        ctk.CTkButton(self.root, text="Logout", command=self.create_login_screen).pack(pady=10)

    def view_logs(self):
        """Displays prediction logs."""
        logs_window = ctk.CTkToplevel(self.root)
        logs_window.title("Prediction Logs")
        logs_window.geometry("800x400")

        tree = ctk.CTkTreeView(logs_window, columns=("Doctor", "Age", "Risk Prediction", "Risk Probability"), show="headings")
        tree.heading("Doctor", text="Doctor")
        tree.heading("Age", text="Age")
        tree.heading("Risk Prediction", text="Risk Prediction")
        tree.heading("Risk Probability", text="Risk Probability")
        tree.pack(fill=ctk.BOTH, expand=True)

        cursor = self.db.cursor()
        cursor.execute('''SELECT u.username, l.age, l.risk_prediction, l.risk_probability
                          FROM logs l
                          JOIN users u ON l.doctor_id = u.id''')
        for row in cursor.fetchall():
            tree.insert("", ctk.END, values=row)

    def add_doctor(self):
        """Adds a new doctor account."""
        add_window = ctk.CTkToplevel(self.root)
        add_window.title("Add Doctor")

        ctk.CTkLabel(add_window, text="Username").grid(row=0, column=0, padx=10, pady=10)
        username_entry = ctk.CTkEntry(add_window)
        username_entry.grid(row=0, column=1)
        ctk.CTkLabel(add_window, text="Password").grid(row=1, column=0, padx=10, pady=10)
        password_entry = ctk.CTkEntry(add_window, show="*")
        password_entry.grid(row=1, column=1)

        def save_doctor():
            username = username_entry.get()
            password = password_entry.get()
            hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            try:
                cursor = self.db.cursor()
                cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, hashed_password, "doctor"))
                self.db.commit()
                messagebox.showinfo("Success", "Doctor added successfully")
                add_window.destroy()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Username already exists")

        ctk.CTkButton(add_window, text="Save", command=save_doctor).grid(row=2, columnspan=2, pady=10)

    def create_doctor_screen(self, doctor_id):
        """Creates the doctor portal."""
        self.clear_screen()
        ctk.CTkLabel(self.root, text="Doctor Portal", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)

        fields = ["Age", "Anaemia", "Creatinine Phosphokinase", "Diabetes",
                  "Ejection Fraction", "High Blood Pressure", "Platelets",
                  "Serum Creatinine", "Serum Sodium", "Sex", "Smoking", "Time"]
        self.entries = {}
        for field in fields:
            ctk.CTkLabel(self.root, text=field).pack()
            entry = ctk.CTkEntry(self.root)
            entry.pack(pady=5)
            self.entries[field] = entry

        def predict():
            try:
                features = [float(self.entries[field].get()) for field in fields]
                prediction, probability = predictor.predict(features)
                with sqlite3.connect(DB_FILE) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''INSERT INTO logs (doctor_id, age, anaemia, creatinine_phosphokinase, diabetes,
                                     ejection_fraction, high_blood_pressure, platelets, serum_creatinine, serum_sodium,
                                     sex, smoking, time, risk_prediction, risk_probability)
                                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                   (doctor_id, *features, prediction, probability))
                    conn.commit()
                messagebox.showinfo("Result", f"Risk: {prediction}\nProbability: {probability:.2f}")
            except ValueError:
                messagebox.showerror("Error", "Invalid input. Please check your entries.")

        ctk.CTkButton(self.root, text="Predict", command=predict).pack(pady=20)
        ctk.CTkButton(self.root, text="Logout", command=self.create_login_screen).pack(pady=10)

    def clear_screen(self):
        """Clears all widgets on the screen."""
        for widget in self.root.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    setup_database()
    predictor = PatientRiskPredictor(DATASET_FILE)
    root = ctk.CTk()
    app = App(root)
    root.mainloop()
