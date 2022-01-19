from datetime import date, time, timedelta

from clocker import tracker, viewer


def main():
    tracker.track(date(2022, 1, 10), time(8,0), time(16, 30), timedelta(minutes=30))
    tracker.track(date(2022, 1, 11), time(8,0), time(17, 30), timedelta(minutes=60))
    tracker.track(date(2022, 1, 12), time(8,0), time(17, 30), timedelta(minutes=30))
    tracker.track(date(2022, 1, 13), time(8,0), time(17, 00), timedelta(minutes=45))
    tracker.track(date(2022, 1, 14), time(8,0), time(15, 30), timedelta(minutes=30))

    viewer.display()

if __name__ == '__main__':
    main()
