# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Facility for displaying information about a Job message to a user.
"""

from googlecloudsdk.api_lib.dataflow import time_util


class DisplayInfo(object):
  """Information about a job displayed in command output.

  Fields:
    id: the job ID
    name: the job name
    type: one of 'batch', 'streaming'
    state: string representing the current job status
    creationTime: in the form yyyy-mm-dd hh:mm:ss
    stateTime: in the form yyyy-mm-dd hh:mm:ss
  """

  def __init__(self, job, dataflow_messages):
    self.id = job.id
    self.name = job.name
    self.type = DisplayInfo._JobTypeForJob(job.type, dataflow_messages)
    self.state = DisplayInfo._StatusForJob(job.currentState, dataflow_messages)

    # We ignore these errors to make the field names more consistent across
    # commands using the --filter argument. This is because most commands are
    # more or less a straight dump of the API response which has camel-case
    # naming conventions. This class is only used for formmating jobs for
    # display purposes.
    #
    # Don't worry, be happy.
    #
    # pylint: disable=invalid-name
    self.stateTime = time_util.FormatTimestamp(job.currentStateTime)
    self.creationTime = time_util.FormatTimestamp(job.createTime)
    # pylint: enable=invalid-name

  @staticmethod
  def _JobTypeForJob(job_type, dataflow_messages):
    """Return a string describing the job type.

    Args:
      job_type: The job type enum
      dataflow_messages: dataflow_messages package
    Returns:
      string describing the job type
    """
    type_value_enum = dataflow_messages.Job.TypeValueValuesEnum
    value_map = {
        type_value_enum.JOB_TYPE_BATCH: 'Batch',
        type_value_enum.JOB_TYPE_STREAMING: 'Streaming',
    }
    return value_map.get(job_type, 'Unknown')

  @staticmethod
  def _StatusForJob(job_state, dataflow_messages):
    """Return a string describing the job state.

    Args:
      job_state: The job state enum
      dataflow_messages: dataflow_messages package
    Returns:
      string describing the job state
    """
    state_value_enum = dataflow_messages.Job.CurrentStateValueValuesEnum
    value_map = {
        state_value_enum.JOB_STATE_CANCELLED: 'Cancelled',
        state_value_enum.JOB_STATE_DONE: 'Done',
        state_value_enum.JOB_STATE_FAILED: 'Failed',
        state_value_enum.JOB_STATE_RUNNING: 'Running',
        state_value_enum.JOB_STATE_STOPPED: 'Stopped',
        state_value_enum.JOB_STATE_UPDATED: 'Updated',
    }
    return value_map.get(job_state, 'Unknown')
