import nose
import os
from nose.plugins import Plugin


class PyPlugin(Plugin):
    """Run tests with all modules in the test folder."""

    def configure(self, options, config):
        Plugin.configure(self, options, config)
        self.enabled = True

    def wantFile(self, filename):
        return filename.endswith('.py')

    def wantDirectory(self, dirname):
        return 'test' in dirname.split(os.path.sep)

    def wantModule(self, filename):
        return True


if __name__ == '__main__':
    nose.main(addplugins=[PyPlugin()])
