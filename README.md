# heart-disease-predictor
Features
Login System with Roles: Supports two user roles—Admin and Doctor. Admins can add new doctor accounts and review prediction logs, while doctors can log in and use the prediction tool.

Patient Risk Prediction: Predicts the probability of heart failure for patients based on several clinical parameters.

Prediction Logs: Saves each prediction with associated doctor information, risk prediction, probability, and timestamp for traceability.

Clean and Modern GUI: Built using customtkinter for a dark-themed, intuitive user experience.

Enhanced Security: Passwords are hashed using bcrypt, and user credentials are stored securely.

Technologies and Libraries Used
Python: Core programming language.

customtkinter & tkinter: For a modern and functional graphical user interface.

SQLite3: Stores user accounts (with secure hashed passwords) and prediction logs in a local database.

pandas: Data manipulation and CSV file handling.

scikit-learn: Implements the RandomForestClassifier for machine learning-based prediction and data preprocessing (train_test_split, StandardScaler).

imbalanced-learn (imblearn): Utilizes SMOTE to address dataset class imbalance, improving model performance.

bcrypt: Hashes user passwords for secure authentication.

Data
Uses the standard Heart Failure Clinical Records Dataset, which includes features such as age, anaemia, creatinine phosphokinase, diabetes, ejection fraction, high blood pressure, platelets, serum creatinine, serum sodium, sex, smoking, and observation time.

How it Works
Admin Setup: On first run, the database is initialized and a default admin user is created.

Training: The system loads the clinical dataset, balances classes with SMOTE, and trains a Random Forest model to predict heart failure risk.

Prediction: Doctors log in and input patient clinical data to receive risk predictions and probabilities. Each prediction is logged to the database.

Admin Review: Admins can view all historical predictions filtered by doctor and patient.

This project is a robust, end-to-end solution for clinical decision support, making advanced predictive analytics accessible and auditable for healthcare providers.
