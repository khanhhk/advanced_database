from pathlib import Path


EXPERIMENTS = Path("experiments")


def test_every_source_directory_has_readme():
    directories = [path for path in EXPERIMENTS.rglob("*")
                   if path.is_dir() and path.name != "__pycache__"
                   and "__pycache__" not in path.parts]
    missing = [str(path) for path in directories if not (path / "README.md").is_file()]
    assert not missing, f"Experiment directories missing README.md: {missing}"


def test_experiment_root_contains_no_workflow_scripts():
    scripts = sorted(path.name for path in EXPERIMENTS.glob("*.py")
                     if path.name != "__init__.py")
    assert scripts == []
