Excellent — now that we have the **correct context** 👏

Luminova isn’t a data annotation platform (that’s likely *another RioEigen product*).
It’s an **AI-powered medical board examination preparation platform** — combining **AI examiners**, **personalized adaptive learning**, and **analytics dashboards** for healthcare professionals.

Let’s properly divide **Luminova** into **Django apps (core + business logic)** and **FastAPI microservices (AI-driven, real-time, and adaptive intelligence features)** — in line with its described functionality.

---

## ⚙️ LUMINOVA ARCHITECTURE OVERVIEW

**Tech Philosophy:**
Luminova uses a **hybrid backend** —

* **Django** manages authentication, user data, learning content, and analytics.
* **FastAPI** powers the AI examiner, real-time performance tracking, and voice/vision-based components.

**Frontend (React/Next.js)** interacts with both, authenticated via Django-issued tokens.

---

## 🧩 DJANGO COMPONENTS

(Main Project: `luminova_core`)

These are the modular **apps under Django**, serving as the platform’s foundation and administrative layer.

---

### 1. `accounts`

**Purpose:** Centralized authentication and user identity management.
**Responsibilities:**

* User registration (doctors, residents, program directors).
* OAuth2/JWT issuance for frontend and FastAPI services.
* Roles: student, instructor, admin, institutional partner.
* Single Sign-On (SSO) for integration with other RioEigen healthcare products.

---

### 2. `institutions`

**Purpose:** Manage academic centers and hospitals using Luminova.
**Responsibilities:**

* Institution registration and verification.
* Manage batches/cohorts of students.
* Role assignment for coordinators and directors.

---

### 3. `specialties`

**Purpose:** Handles medical specialty content modules.
**Responsibilities:**

* Specialty definitions (Anesthesiology, Family Medicine, Radiology, etc.).
* Link questions, cases, and learning materials to each specialty.
* Version control for specialty content updates.

---

### 4. `exam_engine`

**Purpose:** Core exam logic for simulated board assessments.
**Responsibilities:**

* Exam scheduling, attempt tracking, grading.
* Question banks (MCQs, oral exams, case-based simulations).
* Adaptive question selection (based on learner performance).
* Integration with FastAPI “AI Examiner Service”.

---

### 5. `learning`

**Purpose:** Personalized learning pathways.
**Responsibilities:**

* Track user progress, weak areas, and competencies.
* Recommend topics or question sets.
* Manage spaced repetition schedules and adaptive study plans.

---

### 6. `analytics`

**Purpose:** Backend for dashboards and reports.
**Responsibilities:**

* Store exam results, performance scores, and readiness metrics.
* Generate analytics for users and institutions.
* Provide API endpoints for real-time analytics updates (via WebSockets).

---

### 7. `communication`

**Purpose:** Notification and feedback system.
**Responsibilities:**

* In-app notifications and email alerts.
* Instructor–student communication channels.
* Integration with FastAPI speech/voice services for feedback.

---

### 8. `admin_panel`

**Purpose:** Administrative backend for RioEigen and institutional admins.
**Responsibilities:**

* Manage specialties, questions, and AI examiner datasets.
* Monitor user activity and performance analytics.
* Approve content updates and oversee AI model results.

---

### 9. `core`

**Purpose:** System-wide utilities and configuration.
**Responsibilities:**

* Shared mixins, middleware, and constants.
* Logging, caching, Celery, and Redis integrations.
* API gateway for FastAPI services.

---

## 🚀 FASTAPI COMPONENTS

(Independent services optimized for AI/ML, async I/O, and real-time feedback)

---

### 1. `ai_examiner_service`

**Purpose:** Power realistic exam simulations through interactive AI examiners.
**Responsibilities:**

* Handle voice/text-based interactions.
* Use large language models (LLMs) fine-tuned for medical questioning.
* Emotion and tone analysis.
* Real-time question adaptation based on user responses.

---

### 2. `voice_service`

**Purpose:** Speech recognition and voice synthesis for oral exams.
**Responsibilities:**

* Text-to-speech for AI examiner voices.
* Speech-to-text for candidate responses.
* Integrate with AI Examiner via WebSockets for conversational flow.

---

### 3. `vision_service`

**Purpose:** Visual case presentations and analysis.
**Responsibilities:**

* Present medical imagery (X-rays, CT scans, etc.).
* Evaluate user’s diagnostic interpretation via AI-assisted grading.
* Integrate with learning progress (Django `analytics` app).

---

### 4. `personalization_service`

**Purpose:** Adaptive learning and recommendation engine.
**Responsibilities:**

* Analyze user performance data from Django `analytics`.
* Suggest study paths, topics, or difficulty levels.
* Run reinforcement learning algorithms for adaptive difficulty tuning.

---

### 5. `analytics_stream_service`

**Purpose:** Real-time monitoring and data streaming.
**Responsibilities:**

* Receive live exam/interview data from the frontend.
* Push analytics events to Django and dashboards.
* Provide readiness scoring and predictive analysis.

---

### 6. `notification_service`

**Purpose:** Handle asynchronous messaging and alert systems.
**Responsibilities:**

* Push real-time exam updates, reminders, and result notifications.
* Integrate with Celery + message bus (e.g., Kafka, RabbitMQ).

---

## 🔄 COMMUNICATION FLOW SUMMARY

| Source                       | Target               | Medium                                      |
| ---------------------------- | -------------------- | ------------------------------------------- |
| **Frontend (React/Next.js)** | **Django**           | REST (Auth, profile, progress)              |
| **Frontend (React/Next.js)** | **FastAPI**          | WebSocket / REST (exam simulation, AI chat) |
| **Django Core**              | **FastAPI Services** | JWT Auth REST / Message Queue               |
| **FastAPI Services**         | **Django Analytics** | Webhook / Stream updates                    |
| **Django Admin Panel**       | **All services**     | Monitoring and control                      |

---

## 🧠 Summary

| Layer                | Focus                                                    | Technologies                                 |
| -------------------- | -------------------------------------------------------- | -------------------------------------------- |
| **Django Core**      | Authentication, content, analytics, admin, institutions  | Django + DRF + Celery + Redis                |
| **FastAPI Services** | AI examiner, voice/vision AI, personalization, streaming | FastAPI + LLMs + WebSockets + Kafka/RabbitMQ |
| **Frontend**         | User interface for learners, admins, and institutions    | React / Next.js                              |
| **Storage**          | Structured + unstructured                                | PostgreSQL + MinIO/S3 + Redis                |

---

Would you like me to **draw the full architecture diagram** showing:

* Django apps on one side,
* FastAPI microservices on the other,
* and the interaction with the frontend, message bus, and storage layers?

It’ll be perfect for your **proposal document**.
