from toml import load as load_toml


CONFIG = "src/config.toml"


def main():
    config = load_toml(CONFIG)


if __name__ == "__main__":
    main()
