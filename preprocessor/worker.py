from datetime import datetime
from db_helper import DBHelper
import cloudant
import time
import const

class Worker:
    def __init__(self, worker_id: int) -> None:
        self.worker_id = worker_id
        self.db = DBHelper()
    
    def run(self) -> None:
        self.log("start")

        while True:
            
            try:
                self.handle_one()
            except Exception as e:
                self.log("unknown error: ", e)
            
            # TODO: remove this
            break
            time.sleep(0.2)


    def handle_one(self) -> None:
        # get job
        tweet_type = "harvest_twitter_tweet"
        job_id = self.db.get_process_job(tweet_type)
        if job_id is None:
            tweet_type = "import_twitter_tweet"
            job_id = self.db.get_process_job(tweet_type)
            if job_id is None:
                print("no job, wait")
                time.sleep(const.NO_JOB_WAIT)
                return

        # lock job
        try:
            job_doc = self.db.lock_process_job(tweet_type, job_id)
        except Exception as e:
            self.log("unable to lock, skip: ", job_id, e)
            return
        
        try:
            self.process_one(job_doc)
        except Exception as e:
            self.log("error during processing: ", job_id, e)
            return
        
        # mark as finished
        try:
            self.db.mark_as_finished(job_doc)
        except Exception as e:
            self.log("unable to finish a job: ", job_id, e)


    def process_one(self, job_doc: cloudant.document) -> None:
        data = {}

        # do all the things and add results to data

        self.db.submit_result(job_doc, data)

    
    def log(self, *args) -> None:
        t = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print ("[" + t + "] [" + str(self.worker_id) + "]", *args)
