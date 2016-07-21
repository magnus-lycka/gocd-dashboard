from .data_access import get_connection


def get_previous_stage(current_stage):
    result = get_connection().fetch_previous_stage(current_stage.pipeline_name, current_stage.pipeline_counter, current_stage.stage_counter, current_stage.stage_name)
    if result:
        return StageFailureInfo(*result)
    else:
        return None


def get_current_stage(pipeline_name):
    result = get_connection().fetch_current_stage(pipeline_name)
    if result:
        return StageFailureInfo(*result)
    return None


def get_latest_passing_stage(pipeline_name):
    result = get_connection().fetch_latest_passing_stage(pipeline_name)
    if result:
        return StageFailureInfo(*result)
    else:
        return None


def get_first_synced_stage(pipeline_name):
    result = get_connection().fetch_first_synced(pipeline_name)
    if result:
        return StageFailureInfo(*result)
    else:
        return None


def create_stage(pipeline_instance, stage):
    get_connection().insert_stage(pipeline_instance.instance_id, stage)


def create_job(stage, job):
    get_connection().insert_job(stage.stage_id, job)


class PipelineInstance:
    def __init__(self, pipeline_name, pipeline_counter, trigger_message, instance_id):
        self.pipeline_name = pipeline_name
        self.pipeline_counter = pipeline_counter
        self.trigger_message = trigger_message
        self.instance_id = instance_id
        self.stages = {}


class Stage:
    def __init__(self, stage_name, approved_by, stage_result, stage_counter, stage_id, scheduled_date):
        self.stage_name = stage_name
        self.approved_by = approved_by
        self.stage_result = stage_result
        self.stage_counter = stage_counter
        self.stage_id = stage_id
        self.scheduled_date = scheduled_date

    def is_success(self):
        return self.stage_result == "Passed"


class StageFailureInfo:
    def __init__(self, pipeline_name, pipeline_counter, stage_counter, stage_id, stage_name, trigger_message, approved_by, result, failure_stage, responsible, description, scheduled_date):
        self.pipeline_name = pipeline_name
        self.pipeline_counter = pipeline_counter
        self.stage_id = stage_id
        self.stage_name = stage_name
        self.trigger_message = trigger_message
        self.approved_by = approved_by
        self.stage_counter = stage_counter
        self.failure_stage = failure_stage
        self.result = result
        self.responsible = responsible
        self.description = description
        self.scheduled_date = scheduled_date

    def is_success(self):
        return self.result == "Passed"

    def is_claimed(self):
        return self.responsible is not None


class Job:
    def __init__(self, job_name, agent_uuid, scheduled_date, job_id, job_result):
        self.job_name = job_name
        self.agent_uuid = agent_uuid
        self.scheduled_date = scheduled_date
        self.job_id = job_id
        self.job_result = job_result

