import time

def assert_duration(function, min_duration, max_duration):
    start_time = time.time()
    function()
    elapsed_time = time.time() - start_time

    print(elapsed_time)
    assert elapsed_time > min_duration
    assert elapsed_time < max_duration
