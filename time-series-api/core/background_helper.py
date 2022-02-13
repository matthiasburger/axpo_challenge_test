from multiprocessing import Process


def background_job(callback):
    """
    wrapper for starting a background-job
    :param callback: the task to do in the background-process
    """
    task = Process(target=callback())
    task.start()
