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
"""ml models describe command."""

from googlecloudsdk.api_lib.util import http_error_handler
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.ml import flags
from googlecloudsdk.core import apis
from googlecloudsdk.core import resources


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class Describe(base.DescribeCommand):
  """Describe an existing Cloud ML model."""

  def Collection(self):
    return 'ml.models'

  @staticmethod
  def Args(parser):
    """Register flags for this command."""
    flags.GetModelName().AddToParser(parser)

  @http_error_handler.HandleHttpErrors
  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.

    Returns:
      Some value that we want to have printed later.
    """
    client = apis.GetClientInstance('ml', 'v1alpha3')
    res = resources.REGISTRY.Parse(args.model, collection='ml.projects.models')
    req = res.Request()
    resp = client.projects_models.Get(req)
    return resp


@base.ReleaseTracks(base.ReleaseTrack.BETA)
class DescribeBeta(base.DescribeCommand):
  """Describe an existing Cloud ML model."""

  def Collection(self):
    return 'ml.models'

  @staticmethod
  def Args(parser):
    """Register flags for this command."""
    flags.GetModelName().AddToParser(parser)

  @http_error_handler.HandleHttpErrors
  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.

    Returns:
      Some value that we want to have printed later.
    """
    # TODO(b/31062835): remove CloneAndSwitchAPI and extract API code to api_lib
    client = apis.GetClientInstance('ml', 'v1beta1')
    res = resources.REGISTRY.CloneAndSwitchAPIs(client).Parse(
        args.model, collection='ml.projects.models')
    req = res.Request()
    resp = client.projects_models.Get(req)
    return resp
