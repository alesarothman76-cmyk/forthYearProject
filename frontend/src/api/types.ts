export type Role = "ADMIN" | "DOCTOR";

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface ApiError {
  detail: string;
  status_code: number;
  fieldErrors?: Record<string, string[]>;
}

// --- Auth ---

export interface LoginResponse {
  access: string;
  refresh: string;
}

export interface DoctorProfileSummary {
  license_number: string;
  specialization: string;
  phone_number: string;
  registration_status: RegistrationStatus;
}

export interface Me {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: Role;
  is_active: boolean;
  doctor_profile: DoctorProfileSummary | null;
}

export type RegistrationStatus = "PENDING" | "APPROVED" | "REJECTED";

export interface DoctorAdmin {
  id: number;
  username: string;
  email: string;
  is_active: boolean;
  license_number: string;
  specialization: string;
  phone_number: string;
  registration_status: RegistrationStatus;
  reviewed_at: string | null;
  rejection_reason: string;
  created_at: string;
}

// --- Patients ---

export type Gender = "MALE" | "FEMALE";

export type DiseaseSeverity =
  | "NonDemented"
  | "VeryMildDemented"
  | "MildDemented"
  | "ModerateDemented";

export interface Patient {
  id: number;
  national_id: string;
  full_name: string;
  date_of_birth: string;
  gender: Gender;
  email: string;
  medical_history: string;
  current_status: DiseaseSeverity | null;
  created_by_doctor: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AdminPatient {
  id: number;
  national_id: string;
  full_name: string;
  date_of_birth: string;
  gender: Gender;
  email: string;
  current_status: DiseaseSeverity | null;
  created_by_doctor_name: string;
  created_by_doctor_username: string;
  is_active: boolean;
  created_at: string;
}

export interface PatientWritePayload {
  national_id?: string;
  full_name?: string;
  date_of_birth?: string;
  gender?: Gender;
  email?: string;
  medical_history?: string;
}

// --- MRI Scans ---

export type ScanStatus = "PENDING" | "PROCESSING" | "COMPLETED" | "FAILED";

export interface AIAnalysisResult {
  predicted_class: DiseaseSeverity;
  confidence_score: number;
  class_probabilities: Record<DiseaseSeverity, number>;
  model_version: string;
  execution_time_seconds: number;
  heatmap_image: string | null;
}

export interface MRIScan {
  id: number;
  patient: number;
  uploaded_by_doctor: number;
  original_file: string;
  processed_image: string | null;
  dicom_metadata: Record<string, string | string[]> | null;
  status: ScanStatus;
  error_message: string;
  analysis_result: AIAnalysisResult | null;
  results_sent_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface PatientHistoryScan extends MRIScan {
  reports: Report[];
}

export interface PatientHistory {
  patient: Patient;
  scans: PatientHistoryScan[];
}

// --- Reports ---

export type ReportStatus = "DRAFT" | "FINALIZED";

export interface Report {
  id: number;
  mri_scan: number;
  patient_id: number;
  patient_name: string;
  created_by_doctor: number;
  notes: string;
  status: ReportStatus;
  generated_pdf: string | null;
  finalized_at: string | null;
  created_at: string;
  updated_at: string;
}
