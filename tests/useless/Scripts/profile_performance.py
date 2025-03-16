import cProfile
import pstats
from app.main import main

def profile():
    profiler = cProfile.Profile()
    profiler.enable()
    main()
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumtime').print_stats(10)

if __name__ == "__main__":
    profile()