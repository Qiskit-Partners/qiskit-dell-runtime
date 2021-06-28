
from .base import Session, engine, Base
from .runtime_program_model import RuntimeProgram
from .message_model import Message
from .job_model import Job
from sqlalchemy.orm import load_only
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)

ACTIVE="Active"
INACTIVE="Inactive"

class DBService():
    def __init__(self):
        Base.metadata.create_all(engine)

    def save_message(self, job_id, data):
        message = Message()
        message.job_id = job_id
        message.data = data
        message.creation_date = datetime.now()
        session = Session()
        try:
            session.add(message)
            session.commit()
        finally:
            session.close()

    def save_runtime_program(self, runtime_program: RuntimeProgram):
        session = Session()
        try:
            session.add(runtime_program)
            session.commit()
        finally:
            session.close()

    def save_job(self, job: Job):
        session = Session()
        try:
            session.add(job)
            session.commit()
        finally:
            session.close()

    def update_runtime_program(self, program_id, name, data, program_metadata, data_type):
        session = Session()
        try:
            prog = session.query(RuntimeProgram).filter_by(program_id=program_id).one()
            if name:
                setattr(prog, "name", name)
            if data:
                setattr(prog, "data", data)
            if type:
                setattr(prog, "data_type", data_type)
            if program_metadata:
                pm = json.loads(program_metadata)
                meta = json.loads(prog.program_metadata)
                for (key,value) in pm.items():
                    if value:
                        meta[key] = value
                meta_str = json.dumps(meta)
                setattr(prog, "program_metadata", meta_str)
            session.commit()
        finally:
            session.close()

    def update_job_status(self, job_id, status):
        session = Session()
        try:
            job = session.query(Job).filter_by(job_id=job_id).one()
            setattr(job, "status", status)
            session.commit()
        finally:
            session.close()

    def fetch_pod_name(self, job_id):
        try:
            session = Session()
            fields = ['pod_name']
            job = session.query(Job).filter_by(job_id=job_id).options(load_only(*fields)).one()
            return job.pod_name
        finally:
            session.close()

    def delete_runtime_program(self, program_id):
        session = Session()
        try:
            prog = session.query(RuntimeProgram).filter_by(program_id=program_id).one()
            logger.debug(f"Found {prog} with status {prog.status}")
            setattr(prog, "status", INACTIVE)       
            session.commit()
        finally:
            session.close()

    def fetch_messages(self, job_id, timestamp):
        try:
            session = Session()
            fields = ['data', 'creation_date']
            all_messages = session.query(Message).filter_by(job_id=job_id).options(load_only(*fields)).all()
            new_messages = []
            for msg in all_messages:
                if not timestamp or timestamp < msg.creation_date:
                    new_messages.append({"data": msg.data, "timestamp": str(msg.creation_date)})
            return new_messages
        finally:
            session.close()

    def delete_message(self, job_id):
        try:
            session = Session()
            jobs = session.query(Message).filter_by(job_id=job_id).all()
            for job in jobs:
                session.delete(job)
            session.commit()
            return
        finally:
            session.close()
    
    def fetch_runtime_program_data(self, program_id):
        try:
            session = Session()
            fields = ['data', 'data_type']
            program = session.query(RuntimeProgram).filter_by(program_id=program_id).filter_by(status=ACTIVE).options(load_only(*fields)).one()
            resp = {"data": program.data, "data_type": program.data_type}
            return resp
        finally:
            session.close()

    def fetch_runtime_programs(self):
        result = []
        # programs = RuntimeProgram.query.all()
        try:
            session = Session()
            fields = ['program_id', 'name', 'program_metadata']
            programs = session.query(RuntimeProgram).filter_by(status=ACTIVE).options(load_only(*fields)).all()
            logger.debug(f"Found {len(programs)} programs")
            for program in programs:
                result.append({
                    'program_id': program.program_id,
                    'name': program.name,
                    'program_metadata': program.program_metadata
                })
            return result
        finally:
            session.close()

    def fetch_job_status(self, job_id):
        try:
            session = Session()
            fields = ['status']
            job = session.query(Job).filter_by(job_id=job_id).options(load_only(*fields)).one()
            return job.status
        finally:
            session.close()


