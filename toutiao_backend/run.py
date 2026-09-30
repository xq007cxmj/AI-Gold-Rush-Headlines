import sys
from pathlib import Path

if __name__ == "__main__":
    target_dir = str(Path(__file__).resolve().parent.parent)
    if target_dir not in sys.path:
        sys.path.append(target_dir)
        print(f"已将 {target_dir} 添加到 sys.path")

    from toutiao_backend.main import main

    main()
