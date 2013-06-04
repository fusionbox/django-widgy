from optparse import make_option

from django.core.management.base import BaseCommand
from django.core import urlresolvers
from django.contrib.sites.models import Site

from widgy.models import VersionTracker

class Command(BaseCommand):
    """
    Deletes orphaned VersionTrackers, the ones that are left around after
    deleting their owners.

    This command destroys the data necessary to undelete pages, so be careful.
    """
    can_import_settings = True
    option_list = BaseCommand.option_list + (
        make_option('--noinput',
                    action='store_true',
                    dest='force',
                    default=False,
                    help="Don't ask for confirmation before deleting"),
    )

    def handle(self, *args, **options):
        self.force = options['force']

        for tracker in VersionTracker.objects.orphan():
            if self.confirm(tracker):
                tracker.delete()

    def get_confirmation(self, message):
        confirm = raw_input(message)
        if confirm not in ('y', 'n'):
            self.stdout.write('y/n\n')
            return self.get_confirmation(message)
        return confirm == 'y'

    def confirm(self, tracker):
        if self.force:
            return True
        else:
            confirm = self.get_confirmation('delete %s?: ' % self.format_tracker(tracker))
            if not confirm:
                self.stdout.write('skipped\n')
            return confirm

    def format_tracker(self, tracker):
        try:
            url = urlresolvers.reverse('widgy.contrib.widgy_mezzanine.views.preview',
                                       kwargs={'node_pk': tracker.working_copy.pk})
            return 'http://%s%s' % (Site.objects.get_current().domain, url)
        except urlresolvers.NoReverseMatch:
            # maybe widgy_mezzanine isn't installed
            return repr(tracker)
