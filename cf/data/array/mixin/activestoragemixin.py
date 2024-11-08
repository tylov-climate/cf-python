class ActiveStorageMixin:
    """Mixin class for enabling active storage operations.

    .. versionadded:: NEXTVERSION

    """

    @property
    def active_storage(self):
        """Whether active storage operations are allowed.

        Currently, active storage operations are allowed unless the
        data are numerically packed.

        .. versionadded:: NEXTVERSION

        :Returns:

            `bool`
                `True` if active storage operations are allowed,
                otherwise `False`.

        """
        attributes = self.get_attributes({})
        if "add_offset" in attributes or "scale_factor" in attributes:
            return False

        return True
