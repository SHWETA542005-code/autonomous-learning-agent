from graph import build_graph
from curriculum import checkpoints


def main():
    app = build_graph()

    # 🔥 REQUIRED INITIAL STATE
    state = {
        "checkpoint_index": 0,
        "total_checkpoints": len(checkpoints)
    }

    app.invoke(state)


if __name__ == "__main__":
    main()
