import random


def main():
    base_delay = 1
    exponential_factor = 2
    max_delay_seconds = None
    tries = 20
    jitter_seconds = None

    for i in range(1, tries + 1):

        attempt = i

        sleep_delay = base_delay * (exponential_factor**attempt)

        if max_delay_seconds and sleep_delay > max_delay_seconds:
            sleep_delay = max_delay_seconds

        if jitter_seconds:
            jitter = random.randint(-jitter_seconds * 10, jitter_seconds * 10) / 10
            sleep_delay += jitter

        if sleep_delay < 0:
            sleep_delay = 0

        print(round(sleep_delay, 1))


if __name__ == "__main__":
    main()
