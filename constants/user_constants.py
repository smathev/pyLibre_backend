ROLE_USER               = 0 << 0
ROLE_ADMIN              = 1 << 0
ROLE_DOWNLOAD           = 1 << 1
ROLE_UPLOAD             = 1 << 2
ROLE_EDIT               = 1 << 3
ROLE_PASSWD             = 1 << 4
ROLE_ANONYMOUS          = 1 << 5
ROLE_EDIT_SHELFS        = 1 << 6
ROLE_DELETE_BOOKS       = 1 << 7
ROLE_VIEWER             = 1 << 8
ROLE_KOBO_SYNC          = 1 << 9

ALL_ROLES = {
                "admin_role": ROLE_ADMIN,
                "download_role": ROLE_DOWNLOAD,
                "upload_role": ROLE_UPLOAD,
                "edit_role": ROLE_EDIT,
                "passwd_role": ROLE_PASSWD,
                "edit_shelf_role": ROLE_EDIT_SHELFS,
                "delete_role": ROLE_DELETE_BOOKS,
                "viewer_role": ROLE_VIEWER,
                "kobo_sync_role": ROLE_KOBO_SYNC,
            }

DETAIL_RANDOM           = 1 <<  0
SIDEBAR_LANGUAGE        = 1 <<  1
SIDEBAR_SERIES          = 1 <<  2
SIDEBAR_CATEGORY        = 1 <<  3
SIDEBAR_HOT             = 1 <<  4
SIDEBAR_RANDOM          = 1 <<  5
SIDEBAR_AUTHOR          = 1 <<  6
SIDEBAR_BEST_RATED      = 1 <<  7
SIDEBAR_READ_AND_UNREAD = 1 <<  8
SIDEBAR_RECENT          = 1 <<  9
SIDEBAR_SORTED          = 1 << 10
MATURE_CONTENT          = 1 << 11
SIDEBAR_PUBLISHER       = 1 << 12
SIDEBAR_RATING          = 1 << 13
SIDEBAR_FORMAT          = 1 << 14
SIDEBAR_ARCHIVED        = 1 << 15
SIDEBAR_DOWNLOAD        = 1 << 16
SIDEBAR_LIST            = 1 << 17

sidebar_settings = {
                "detail_random": DETAIL_RANDOM,
                "sidebar_language": SIDEBAR_LANGUAGE,
                "sidebar_series": SIDEBAR_SERIES,
                "sidebar_category": SIDEBAR_CATEGORY,
                "sidebar_random": SIDEBAR_RANDOM,
                "sidebar_author": SIDEBAR_AUTHOR,
                "sidebar_best_rated": SIDEBAR_BEST_RATED,
                "sidebar_read_and_unread": SIDEBAR_READ_AND_UNREAD,
                "sidebar_recent": SIDEBAR_RECENT,
                "sidebar_sorted": SIDEBAR_SORTED,
                "sidebar_publisher": SIDEBAR_PUBLISHER,
                "sidebar_rating": SIDEBAR_RATING,
                "sidebar_format": SIDEBAR_FORMAT,
                "sidebar_archived": SIDEBAR_ARCHIVED,
                "sidebar_download": SIDEBAR_DOWNLOAD,
                "sidebar_list": SIDEBAR_LIST,
            }


ADMIN_USER_ROLES        = sum(r for r in ALL_ROLES.values()) & ~ROLE_ANONYMOUS
ADMIN_USER_SIDEBAR      = (SIDEBAR_LIST << 1) - 1


DEFAULT_PASSWORD    = "admin123"  # nosec
DEFAULT_USERLEVEL   = ROLE_USER