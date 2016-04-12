from tests.bucket_update.test_base import TestBase


class SearchUpdaterTest(TestBase):
    def test_all(self):
        """
            Supposed to be a generic test that will check that
            metadata is created, updated and deleted in the
            search layer.
        """

        # metadata only in the cloud should be added to search
        add_builder = self.create_metadata_builder() \
            .property("test", "test") \
            .resource_url("/test/artifact/kyle-test/add")
        self.add_cloud(add_builder)
        self.add_cloud_artifact(add_builder)

        # metadata only in the search layer should be deleted.
        delete_builder = self.create_metadata_builder() \
            .resource_url("/test/artifact/lyle-test/delete-me")

        self.add_search(delete_builder)

        # metadata in both should get updated
        update_search_builder = self.create_metadata_builder() \
            .property("lol", "not-lol") \
            .resource_url("/test/artifact/jyle-test/needs-update")

        update_cloud_builder = update_search_builder \
            .copy() \
            .property("lol", "is-lol")

        self.add_search(update_search_builder)
        self.add_cloud(update_cloud_builder)
        self.add_cloud_artifact(update_cloud_builder)

        # Important because if these docs were JUST added
        # to elasticsearch they will not end up being found
        # when doing the bulk update.  In practice this shouldn't
        # happen unless in very quick succession we add metadata
        # then manually delete it in S3 and then run bucket-update
        # really really quick.
        self.search_wrapper.refresh_index()

        # Running actual code
        runner = self.container.search_updater
        runner.run()

        # These two artifacts should have identity metadata in both
        # search and cloud
        self.assert_metadata_matches(add_builder.identity.resource_url)
        self.assert_metadata_matches(update_search_builder.identity.resource_url)

        # This should have been deleted
        should_be_deleted = self.search_wrapper.get_metadata(delete_builder.identity.search)
        self.assertEqual(None, should_be_deleted)
