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
"""Implementation of gcloud dataflow metrics list command.
"""

import re

from apitools.base.py import exceptions

from googlecloudsdk.api_lib.dataflow import dataflow_util
from googlecloudsdk.api_lib.dataflow import job_utils
from googlecloudsdk.api_lib.dataflow import time_util
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions as calliope_exceptions
from surface import dataflow as commands


class List(base.ListCommand):
  """Retrieves the metrics from a specific job.

  This command can be used to explore the job's metrics at a fine-grained level.

  ## EXAMPLES

  Filter metrics with the given name:

    $ {command} --filter="name=ElementCount"

  Filter child metrics with matching transforms:

    $ {command} --transform=WordCount

  Filter child output metrics:

    $ {command} --transform=WordCount/Write.*out

  Filter all output metrics:

    $ {command} --transform=.*out

  Filter all custom-defined user metrics

    $ {command} --source=user

  Filter metrics with a scalar value greater than a threshold.

    $ {command} --filter="scalar > 50"
  """

  USER_SOURCE = 'user'
  SERVICE_SOURCE = 'service'

  @staticmethod
  def Args(parser):
    """Register flags for this command."""
    job_utils.ArgsForJobRef(parser)

    base.FLATTEN_FLAG.RemoveFromParser(parser)
    base.PAGE_SIZE_FLAG.RemoveFromParser(parser)
    base.SORT_BY_FLAG.RemoveFromParser(parser)
    base.URI_FLAG.RemoveFromParser(parser)

    parser.add_argument(
        '--changed-after',
        type=time_util.ParseTimeArg,
        help='Only display metrics that have changed after the given time')
    parser.add_argument(
        '--hide-committed',
        default=False,
        action='store_true',
        help='If true, hide committed values.')
    parser.add_argument(
        '--transform',
        help='Filters only the metrics that prefix match the given regex.')
    parser.add_argument(
        '--source',
        choices=['all', 'user', 'service'],
        default='all',
        help=('Can be either "all", "user", or "service". By default, source '
              'is "all" and retrieves all metrics. If set to user, displays '
              'only custom user metrics. If set to service, displays only '
              'dataflow service metrics.'))
    parser.add_argument(
        '--tentative',
        default=False,
        action='store_true',
        help='If true, display tentative values.')

  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: all the arguments that were provided to this command invocation.

    Returns:
      None on success, or a string containing the error message.
    """
    apitools_client = self.context[commands.DATAFLOW_APITOOLS_CLIENT_KEY]
    dataflow_messages = self.context[commands.DATAFLOW_MESSAGES_MODULE_KEY]
    job_ref = job_utils.ExtractJobRef(self.context, args.job)

    start_time = args.changed_after and time_util.Strftime(args.changed_after)
    request = dataflow_messages.DataflowProjectsJobsGetMetricsRequest(
        projectId=job_ref.projectId, jobId=job_ref.jobId, startTime=start_time)

    preds = []
    if not args.tentative and args.hide_committed:
      raise calliope_exceptions.ToolException(
          'Cannot exclude both tentative and committed metrics.')
    elif not args.tentative and not args.hide_committed:
      preds.append(lambda m: self._GetContextValue(m, 'tentative') != 'true')
    elif args.tentative and args.hide_committed:
      preds.append(lambda m: self._GetContextValue(m, 'tentative') == 'true')

    preds.append(lambda m: self._FilterBySource(m, args.source))
    preds.append(lambda m: self._FilterByTransform(m, args.transform))

    if args.changed_after:
      preds.append(
          lambda m: time_util.ParseTimeArg(m.updateTime) > args.changed_after)

    try:
      response = apitools_client.projects_jobs.GetMetrics(request)
    except exceptions.HttpError as error:
      raise dataflow_util.MakeErrorMessage(error, job_ref.jobId,
                                           job_ref.projectId)

    return [self._Format(m) for m in response.metrics
            if all([pred(m) for pred in preds])]

  def _IsSentinelWatermark(self, metric):
    """This returns true if the metric is a watermark with a sentinel value.

    Args:
      metric: A single UpdateMetric returned from the API.
    Returns:
      True if the metric is a sentinel value, false otherwise.
    """
    # Currently, we only apply the change from kInt64(MAX|MIN) to sentinel
    # values from dataflow metrics.

    if not dataflow_util.DATAFLOW_METRICS_RE.match(metric.name.origin):
      return False
    if not dataflow_util.WINDMILL_WATERMARK_RE.match(metric.name.name):
      return False
    return (metric.scalar.integer_value == -1 or
            metric.scalar.integer_value == -2)

  def _GetWatermarkSentinelDescription(self, metric):
    """This method gets the description of the watermark sentinel value.

    There are only two watermark sentinel values we care about, -1 represents a
    watermark at kInt64Min. -2 represents a watermark at kInt64Max. This runs
    on the assumption that _IsSentinelWatermark was called first.

    Args:
      metric: A single UpdateMetric returned from the API.
    Returns:
      The sentinel description.
    """
    value = metric.scalar.integer_value
    if value == -1:
      return 'Unknown watermark'
    return 'Max watermark'

  def _Format(self, metric):
    """Performs extra formatting for sentinel values or otherwise.

    Args:
      metric: A single UpdateMetric returned from the API.
    Returns:
      The formatted metric.
    """
    if self._IsSentinelWatermark(metric):
      metric.scalar.string_value = self._GetWatermarkSentinelDescription(metric)
      metric.scalar.reset('integer_value')
    return metric

  def _FilterByTransform(self, metric, transform):
    output_user_name = self._GetContextValue(metric, 'output_user_name') or ''
    step = self._GetContextValue(metric, 'step') or ''
    transform = re.compile(transform or '')
    if transform.match(output_user_name) or transform.match(step):
      return True
    return False

  def _FilterBySource(self, metric, source):
    if source == self.USER_SOURCE:
      return metric.name.origin == 'user'
    elif source == self.SERVICE_SOURCE:
      return metric.name.origin == 'dataflow/v1b3'
    return True

  def _GetContextValue(self, metric, key):
    if metric.name.context:
      for prop in metric.name.context.additionalProperties:
        if prop.key == key:
          return prop.value
    return None
