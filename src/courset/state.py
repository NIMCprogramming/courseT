from pathlib import Path

from courset.models import MissedConcept, UserProgress


class ProgressStore:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> UserProgress:
        if not self.path.exists():
            return UserProgress()
        return UserProgress.model_validate_json(self.path.read_text())

    def save(self, progress: UserProgress) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(progress.model_dump_json(indent=2))
        temporary.replace(self.path)

    def reset(self) -> None:
        self.path.unlink(missing_ok=True)

    def record_missed(self, progress: UserProgress, concept: str, lesson_id: str) -> None:
        if not concept:
            return
        for entry in progress.missed_concepts:
            if entry.concept == concept and entry.lesson_id == lesson_id:
                entry.count += 1
                self.save(progress)
                return
        progress.missed_concepts.append(MissedConcept(concept=concept, lesson_id=lesson_id))
        self.save(progress)
