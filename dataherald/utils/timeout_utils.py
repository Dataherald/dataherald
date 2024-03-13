import threading


def run_with_timeout(func, args=(), kwargs=None, timeout_duration=60):
    if kwargs is None:
        kwargs = {}

    def func_wrapper(result_container):
        try:
            result_container.append(func(*args, **kwargs))
        except Exception as e:
            result_container.append(e)

    result_container = []
    thread = threading.Thread(target=func_wrapper, args=(result_container,))
    thread.start()
    thread.join(timeout=timeout_duration)
    if thread.is_alive():
        raise TimeoutError("Function execution exceeded the timeout")
    if result_container:
        if isinstance(result_container[0], Exception):
            raise result_container[0]
        return result_container[0]
    raise TimeoutError("Function execution exceeded the timeout")
