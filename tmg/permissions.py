#
# Copyright Olivier Aubert <contact@olivieraubert.net> 2013
#
# This software offers a media transcoding and processing platform.
#
# TMG is a free software subjected to a double license.
# You can redistribute it and/or modify if you respect the terms of either
# (at least one of both licenses):
# - the GNU Lesser General Public License as published by the Free Software Foundation;
#   either version 3 of the License, or any later version.
# - the CeCILL-C as published by CeCILL; either version 2 of the License, or any later version.
#
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_permission(self, request, view, obj=None):
        # Skip the check unless this is an object-level test
        if obj is None:
            return True

        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:            
            return True

        # Write permissions are only allowed to the owner of the snippet
        return obj.owner == request.user
