from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Creates the required ReviewedVersionCommit objects when migrating to a ReviewedWidgySite'

    def handle(self, *args, **options):
        # XXX: why doesn't this work at the top-level?
        from widgy.models.versioning import VersionCommit
        from widgy.contrib.review_queue.models import ReviewedVersionCommit

        for commit in VersionCommit.objects.filter(reviewedversioncommit=None):
            new_commit = ReviewedVersionCommit(
                versioncommit_ptr=commit,
                approved_at=commit.created_at,
                approved_by_id=commit.author_id,
            )
            new_commit.__dict__.update(commit.__dict__)
            new_commit.save()
