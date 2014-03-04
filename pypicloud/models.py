""" Model objects """
import pkg_resources

import os
import re
from .compat import total_ordering


def normalize_name(name):
    """ Normalize a python package name """
    return name.lower().replace('-', '_')


@total_ordering
class Package(object):

    """
    Representation of a versioned package

    Parameters
    ----------
    name : str
        The name of the package (will be normalized)
    version : str
        The version number of the package
    path : str
        The absolute S3 path of the package file
    last_modified : datetime
        The datetime when this package was uploaded
    data : dict
        Metadata about the package

    """

    def __init__(self, name, version, path, last_modified, **kwargs):
        self.name = normalize_name(name)
        self.version = version
        self.path = path
        self.last_modified = last_modified
        self.data = kwargs

    @property
    def filename(self):
        """ Getter for raw filename with no prefixes """
        return os.path.basename(self.path)

    def get_url(self, request):
        """ Create path to the download link """
        return request.db.get_url(self)

    @property
    def is_prerelease(self):
        """ Returns True if the version is a prerelease version """
        return re.match(r'^\d+(\.\d+)*$', self.version) is None

    def __hash__(self):
        return hash(self.name) + hash(self.version)

    def __eq__(self, other):
        return self.name == other.name and self.version == other.version

    def __lt__(self, other):
        return ((self.name, pkg_resources.parse_version(self.version)) <
                (other.name, pkg_resources.parse_version(other.version)))

    def __repr__(self):
        return unicode(self)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return u'Package(%s, %s)' % (self.name, self.version)

    def __json__(self, request):
        return {
            'name': self.name,
            'last_modified': self.last_modified,
            'version': self.version,
            'url': self.get_url(request),
        }
