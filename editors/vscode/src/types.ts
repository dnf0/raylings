export interface ExerciseData {
  name: string;
  title: string;
  path: string;
  chapter_name: string;
  chapter_number: number;
  hints: string[];
  requires_cluster: boolean;
  completed: boolean;
  has_marker: boolean;
  exists: boolean;
}

export interface ChapterData {
  number: number;
  name: string;
  title: string;
  description: string;
  exercises: ExerciseData[];
}

export interface ListResponse {
  version: string;
  total_exercises: number;
  chapters: ChapterData[];
}

export interface ProgressResponse {
  total: number;
  completed: number;
  percentage: number;
  current_exercise: string | null;
  current_path: string | null;
  is_finished: boolean;
}

export interface RunResponse {
  name: string;
  title: string;
  path: string;
  passed: boolean;
  has_not_done_marker: boolean;
  exit_code: number;
  output: string;
  error: string | null;
}

export interface HintResponse {
  name: string;
  title: string;
  hints: string[];
  selected_level: number;
  selected_hint: string;
}
