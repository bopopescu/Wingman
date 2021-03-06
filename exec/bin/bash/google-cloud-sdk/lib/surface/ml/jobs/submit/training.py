# Copyright 2016 Google Inc. All Rights Reserved.
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
"""ml jobs submit training command."""

from googlecloudsdk.api_lib.ml import jobs
from googlecloudsdk.api_lib.ml import jobs_v1beta1
from googlecloudsdk.api_lib.ml import operations
from googlecloudsdk.api_lib.util import http_error_handler
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.ml import flags
from googlecloudsdk.core import apis


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class Train(base.Command):
  """Start a Cloud ML training job."""

  @staticmethod
  def Args(parser):
    """Register flags for this command."""
    flags.JOB_NAME.AddToParser(parser)
    flags.MODULE_NAME.AddToParser(parser)
    flags.TRAINER_URI.AddToParser(parser)
    flags.CONFIG.AddToParser(parser)
    base.ASYNC_FLAG.AddToParser(parser)

  @http_error_handler.HandleHttpErrors
  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.

    Returns:
      Some value that we want to have printed later.
    """
    config = jobs.BuildTrainingConfig(
        path=args.config,
        module_name=args.module,
        job_name=args.job,
        trainer_uri=args.trainer_uri)
    op = jobs.Train(config)
    if args.async:
      return op
    return operations.WaitForOperation(
        apis.GetClientInstance('ml', 'v1alpha3').projects_operations, op)


@base.ReleaseTracks(base.ReleaseTrack.BETA)
class BetaTrain(base.Command):
  """Start a Cloud ML training job."""

  @staticmethod
  def Args(parser):
    """Register flags for this command."""
    flags.JOB_NAME.AddToParser(parser)
    flags.MODULE_NAME.AddToParser(parser)
    flags.TRAINER_URI.AddToParser(parser)
    flags.REGION.AddToParser(parser)
    flags.CONFIG.AddToParser(parser)

  @http_error_handler.HandleHttpErrors
  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.

    Returns:
      Some value that we want to have printed later.
    """
    job = jobs_v1beta1.BuildTrainingJob(
        path=args.config,
        module_name=args.module,
        job_name=args.job,
        trainer_uri=args.trainer_uri,
        region=args.region)
    return jobs_v1beta1.Create(job)
