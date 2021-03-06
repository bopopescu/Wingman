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
"""Resource definitions for cloud platform apis."""

import enum

<%!
def SplitPath(path, max_length):
  """Splits path into chunks of max_length."""
  parts = []
  while path:
    if len(path) < max_length:
      index = max_length
    else:
      # Prefer to split on last '/'.
      index = path.rfind('/', 0, max_length - 1)
      if index < 0:
        index = min(max_length - 1, len(path) - 1)
    parts.append(path[:index+1])
    path = path[index+1:]
  return parts
%>
class Collections(enum.Enum):
  """Collections for all supported apis."""

% for collection_info in collections:
  ${collection_info.api_name.replace('-', '_').upper()}_\
${collection_info.api_version.upper()}_\
${collection_info.name.upper().replace('.', '_')} = (
      '${collection_info.api_name}',
      '${collection_info.api_version}',
      '${collection_info.base_url}',
      '${collection_info.name}',
% for i, part in enumerate(SplitPath(collection_info.path, 80 - 3 - 6)):
% if i:

% endif
      '${part}'\
% endfor
,
      ${collection_info.params})
% endfor

  def __init__(self, api_name, api_version, base_url,
               collection_name, path, params):
    self.api_name = api_name
    self.api_version = api_version
    self.base_url = base_url
    self.collection_name = collection_name
    self.path = path
    self.params = params
