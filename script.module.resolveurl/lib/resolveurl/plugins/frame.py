"""
    Plugin for ResolveURL
    Copyright (C) 2025 gujal

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import json
import re
from six.moves import urllib_parse
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class FrameResolver(ResolveUrl):
    name = 'Frame'
    domains = ['f.io']
    pattern = r'(?://|\.)(f\.io)/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        headers = {'User-Agent': common.FF_USER_AGENT}
        web_url = helpers.get_redirect_url(self.get_url(host, media_id), headers=headers)
        web_url = helpers.get_redirect_url(web_url, headers=headers)
        ref = urllib_parse.urljoin(web_url, '/')
        headers.update({
            'Referer': ref,
            'Origin': ref[:-1]
        })
        aid = web_url.split('/')[-1]
        sid = web_url.split('/')[-3]
        aurl = 'https://api.frame.io/graphql'
        result = self.search_asset(aurl, headers, aid, sid)
        if result:
            return result + helpers.append_headers(headers)

        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'https://{host}/{media_id}')

    @staticmethod
    def gqlmin(q):
        q = re.sub(' {4}', '', q)
        return q

    def search_asset(self, api_url, hdrs, asset_id, share_id):
        variables = {
            'sortBys': [],
            'assetIds': [asset_id]
        }
        query = '''
            query GetAssetsForViewer($assetIds: [ID!]!, $sortBys: [MetadataSortByInput!] = []) @stewardship(stewards: [VIEWER]) {
            assets(assetIds: $assetIds) {
                ...Transcriptions
                ...AssetForViewerOrFinderData
                ...AssetContentCredentials
                __typename
            }
            }

            fragment Transcriptions on Asset {
            id
            ... on VideoAsset {
                localeTranscriptions(page: {first: 100}) {
                nodes {
                    id
                    name
                    displayName
                    encodeStatus
                    ...TranscriptUrls
                    locale
                    lastEditedAt
                    source
                    __typename
                }
                __typename
                }
                __typename
            }
            ... on AudioAsset {
                localeTranscriptions(page: {first: 100}) {
                nodes {
                    id
                    name
                    displayName
                    encodeStatus
                    ...TranscriptUrls
                    locale
                    lastEditedAt
                    source
                    __typename
                }
                __typename
                }
                __typename
            }
            __typename
            }

            fragment TranscriptUrls on Transcription {
            json {
                streamUrl
                __typename
            }
            vtt {
                downloadUrl
                __typename
            }
            srt {
                downloadUrl
                __typename
            }
            text {
                downloadUrl
                __typename
            }
            __typename
            }

            fragment AssetForViewerOrFinderData on Asset {
            assetType
            commentCount
            creator {
                id
                __typename
            }
            id
            insertedAt
            name
            parent {
                id
                __typename
            }
            project {
                id
                workspace {
                id
                accountId
                __typename
                }
                __typename
            }
            status
            isWatermarked
            ...AssetMediaThumbnailInfo
            ...AssetWithFieldValues
            ...DeviceLinkOnAssetTransfer
            ...AssetForensicallyWatermarked
            ...Temporary3DModelInfo
            ... on FolderAsset {
                itemCount
                matchingChildren(
                filters: []
                flattenFolders: false
                groupBys: []
                page: {afterOffset: 0, first: 3, mode: OFFSET}
                sortBys: $sortBys
                ) {
                nodes {
                    id
                    ... on VersionStackAsset {
                    versions {
                        id
                        __typename
                    }
                    __typename
                    }
                    __typename
                }
                __typename
                }
                __typename
            }
            ... on VersionStackAsset {
                versions {
                assetType
                id
                insertedAt
                __typename
                }
                __typename
            }
            ... on DocumentAsset {
                commentCountPerPage {
                pageNumber
                commentCount
                __typename
                }
                __typename
            }
            ... on VideoAsset {
                frameGrabEnabled
                __typename
            }
            ... on UnsupportedAsset {
                isInteractiveEligible
                __typename
            }
            ... on InteractiveAsset {
                ...CommentCountPerUrl
                media {
                id
                manifest {
                    basePath
                    downloadUrl
                    rootPath
                    paths {
                    path
                    thumbnail
                    dimensions {
                        width
                        height
                        __typename
                    }
                    __typename
                    }
                    __typename
                }
                interactiveTranscodes {
                    encodeStatus
                    key
                    __typename
                }
                __typename
                }
                __typename
            }
            __typename
            }

            fragment AssetMediaThumbnailInfo on Asset {
            ...AssetMediaThumbnailInfoPrivate
            filesize
            id
            name
            status
            commentCount
            ... on VersionStackAsset {
                versions {
                ...AssetMediaThumbnailInfoPrivate
                id
                filesize
                name
                status
                commentCount
                versionNumber
                __typename
                }
                __typename
            }
            __typename
            }

            fragment AssetMediaThumbnailInfoPrivate on Asset {
            ... on AudioAsset {
                media {
                ...CompleteAudioMedia
                fps
                id
                ...MediaTranscodesPrivateForAssetMediaThumbnailInfo
                mimeType
                __typename
                }
                thumbnailImageUrl {
                url
                __typename
                }
                thumbTranscodes {
                ...ThumbTranscodesInfoPrivateForAssetMediaThumbnailInfo
                __typename
                }
                __typename
            }
            ... on DocumentAsset {
                media {
                ...CompleteDocumentMedia
                id
                ...MediaTranscodesPrivateForAssetMediaThumbnailInfo
                mimeType
                thumbScrubSprite {
                    frames
                    streamUrl
                    tileX
                    tileY
                    __typename
                }
                __typename
                }
                thumbnailImageUrl {
                url
                __typename
                }
                thumbTranscodes {
                ...ThumbTranscodesInfoPrivateForAssetMediaThumbnailInfo
                __typename
                }
                __typename
            }
            ... on ImageAsset {
                media {
                ...CompleteImageMedia
                id
                ...MediaTranscodesPrivateForAssetMediaThumbnailInfo
                metadata {
                    id
                    originalHeight
                    originalWidth
                    hasAlpha
                    __typename
                }
                mimeType
                __typename
                }
                thumbnailImageUrl {
                url
                __typename
                }
                thumbTranscodes {
                ...ThumbTranscodesInfoPrivateForAssetMediaThumbnailInfo
                __typename
                }
                __typename
            }
            ... on InteractiveAsset {
                media {
                ...CompleteInteractiveMedia
                id
                mimeType
                __typename
                }
                thumbnailImageUrl {
                url
                __typename
                }
                __typename
            }
            ... on UnsupportedAsset {
                media {
                ...CompleteUnsupportedMedia
                id
                ...MediaTranscodesPrivateForAssetMediaThumbnailInfo
                mimeType
                __typename
                }
                __typename
            }
            ... on VideoAsset {
                media {
                ...CompleteVideoMedia
                id
                imageTranscodes {
                    downloadUrl
                    encodeStatus
                    key
                    streamUrl
                    __typename
                }
                ...MediaTranscodesPrivateForAssetMediaThumbnailInfo
                metadata {
                    id
                    hasAudio
                    originalHeight
                    originalWidth
                    __typename
                }
                mimeType
                thumbScrubSprite {
                    frames
                    streamUrl
                    tileX
                    tileY
                    __typename
                }
                __typename
                }
                thumbnailImageUrl {
                url
                __typename
                }
                thumbTranscodes {
                ...ThumbTranscodesInfoPrivateForAssetMediaThumbnailInfo
                __typename
                }
                __typename
            }
            __typename
            }

            fragment CompleteAudioMedia on AudioMedia {
            audioTranscodes {
                downloadUrl
                encodeStatus
                key
                streamUrl
                __typename
            }
            duration
            filesize
            fps
            hlsManifest
            id
            insertedAt
            mimeType
            original {
                ...OriginalMediaInfo
                __typename
            }
            transcodedAt
            __typename
            }

            fragment OriginalMediaInfo on OriginalInfo {
            key
            downloadUrl
            filesizeInBytes
            inlineUrl
            codec
            __typename
            }

            fragment MediaTranscodesPrivateForAssetMediaThumbnailInfo on Media {
            checksums {
                xxHash
                __typename
            }
            mimeType
            transcodedAt
            __typename
            }

            fragment ThumbTranscodesInfoPrivateForAssetMediaThumbnailInfo on ThumbTranscodeInfo {
            encodeStatus
            key
            streamUrl
            __typename
            }

            fragment CompleteDocumentMedia on DocumentMedia {
            ...CompleteDocumentMediaWithoutPdfTranscode
            pdfProxyTranscode {
                url
                encodeStatus
                __typename
            }
            pdfDownload {
                url
                __typename
            }
            __typename
            }

            fragment CompleteDocumentMediaWithoutPdfTranscode on DocumentMedia {
            filesize
            id
            insertedAt
            metadata {
                id
                originalHeight
                originalWidth
                baseUrl
                __typename
            }
            mimeType
            original {
                ...OriginalMediaInfo
                __typename
            }
            pageCount
            pages {
                ...DocumentPage
                __typename
            }
            __typename
            }

            fragment DocumentPage on Page {
            height
            width
            __typename
            }

            fragment CompleteImageMedia on ImageMedia {
            filesize
            id
            imageTranscodes {
                downloadUrl
                encodeStatus
                key
                streamUrl
                __typename
            }
            insertedAt
            metadata {
                id
                originalHeight
                originalWidth
                hasAlpha
                __typename
            }
            mimeType
            original {
                ...OriginalMediaInfo
                __typename
            }
            __typename
            }

            fragment CompleteInteractiveMedia on InteractiveMedia {
            filesize
            id
            insertedAt
            mimeType
            original {
                ...OriginalMediaInfo
                __typename
            }
            __typename
            }

            fragment CompleteUnsupportedMedia on UnsupportedMedia {
            filesize
            id
            insertedAt
            mimeType
            original {
                ...OriginalMediaInfo
                __typename
            }
            __typename
            }

            fragment CompleteVideoMedia on VideoMedia {
            drm {
                fairplayStreamingCertificateUrl
                fairplayStreamingLicenseUrl
                widevineLicenseUrl
                __typename
            }
            duration
            filesize
            fps
            frames
            hlsManifest
            id
            imageTranscodes {
                downloadUrl
                encodeStatus
                key
                streamUrl
                __typename
            }
            insertedAt
            metadata {
                id
                originalHeight
                originalWidth
                isVfr
                __typename
            }
            mimeType
            original {
                ...OriginalMediaInfo
                __typename
            }
            timecode
            transcodedAt
            videoTranscodes {
                codec
                downloadUrl
                encodeStatus
                filesizeInBytes
                height
                key
                streamUrl
                required
                width
                __typename
            }
            __typename
            }

            fragment AssetWithFieldValues on Asset {
            id
            ...AssetsForAssetWithFieldValuesPrivate
            ... on VersionStackAsset {
                versions {
                ...AssetsForAssetWithFieldValuesPrivate
                id
                __typename
                }
                __typename
            }
            __typename
            }

            fragment AssetsForAssetWithFieldValuesPrivate on Asset {
            ... on AudioAsset {
                ...FieldValuesForAssetWithFieldValuesPrivate
                __typename
            }
            ... on DocumentAsset {
                ...FieldValuesForAssetWithFieldValuesPrivate
                __typename
            }
            ... on ImageAsset {
                ...FieldValuesForAssetWithFieldValuesPrivate
                __typename
            }
            ... on InteractiveAsset {
                ...FieldValuesForAssetWithFieldValuesPrivate
                __typename
            }
            ... on UnsupportedAsset {
                ...FieldValuesForAssetWithFieldValuesPrivate
                __typename
            }
            ... on VideoAsset {
                ...FieldValuesForAssetWithFieldValuesPrivate
                __typename
            }
            __typename
            }

            fragment FieldValuesForAssetWithFieldValuesPrivate on Collectible {
            fieldValues: fieldValuesNew(page: {first: 50}) {
                nodes {
                ...AssetFieldValueInfo
                __typename
                }
                totalCount
                __typename
            }
            __typename
            }

            fragment AssetFieldValueInfo on AssetFieldValue {
            fieldDefinition {
                id
                __typename
            }
            fieldType
            id
            isValueTrimmed
            value {
                ...FieldValueInfo
                __typename
            }
            __typename
            }

            fragment FieldValueInfo on FieldValue {
            ... on LongTextFieldValue {
                longText
                __typename
            }
            ... on NumberFieldValue {
                number
                __typename
            }
            ... on RatingFieldValue {
                rating
                __typename
            }
            ... on SelectFieldValue {
                selectedOptions
                __typename
            }
            ... on SelectMultiFieldValue {
                multiSelectedOptions
                __typename
            }
            ... on TextFieldValue {
                text
                __typename
            }
            ... on ToggleFieldValue {
                toggle
                __typename
            }
            ... on DateFieldValue {
                date
                __typename
            }
            ... on UsersFieldValue {
                selectedMembers {
                displayName
                id
                ... on UserSelectMemberValue {
                    avatarColor
                    color
                    displayImageUrl
                    __typename
                }
                ... on AccountUserGroupSelectMemberValue {
                    emoji
                    __typename
                }
                __typename
                }
                selectedUsers {
                id
                type
                __typename
                }
                __typename
            }
            ... on UserSingleFieldValue {
                singleSelectedMember {
                displayName
                id
                ... on UserSelectMemberValue {
                    color
                    displayImageUrl
                    __typename
                }
                ... on AccountUserGroupSelectMemberValue {
                    emoji
                    __typename
                }
                __typename
                }
                __typename
            }
            ... on UserMultiFieldValue {
                multiSelectedMembers {
                displayName
                id
                ... on UserSelectMemberValue {
                    color
                    displayImageUrl
                    __typename
                }
                ... on AccountUserGroupSelectMemberValue {
                    emoji
                    __typename
                }
                __typename
                }
                __typename
            }
            __typename
            }

            fragment DeviceLinkOnAssetTransfer on Asset {
            ... on AudioAsset {
                deviceLink {
                id
                __typename
                }
                __typename
            }
            ... on DocumentAsset {
                deviceLink {
                id
                __typename
                }
                __typename
            }
            ... on ImageAsset {
                deviceLink {
                id
                __typename
                }
                __typename
            }
            ... on VideoAsset {
                deviceLink {
                id
                __typename
                }
                __typename
            }
            ... on UnsupportedAsset {
                deviceLink {
                id
                __typename
                }
                __typename
            }
            __typename
            }

            fragment AssetForensicallyWatermarked on VideoAsset {
            id
            forensicallyWatermarked
            __typename
            }

            fragment Temporary3DModelInfo on Asset {
            id
            ... on VideoAsset {
                media {
                id
                metadata {
                    id
                    isModel
                    __typename
                }
                __typename
                }
                __typename
            }
            __typename
            }

            fragment CommentCountPerUrl on InteractiveAsset {
            commentCountPerUrl {
                viewerUrl
                commentCount
                __typename
            }
            __typename
            }

            fragment AssetContentCredentials on Asset {
            id
            ... on AudioAsset {
                media {
                id
                metadata {
                    id
                    contentAuthenticity {
                    credentials {
                        hasCredentials
                        inspectUrl
                        aiStatus
                        __typename
                    }
                    __typename
                    }
                    __typename
                }
                __typename
                }
                __typename
            }
            ... on VideoAsset {
                media {
                id
                metadata {
                    id
                    contentAuthenticity {
                    credentials {
                        hasCredentials
                        inspectUrl
                        aiStatus
                        __typename
                    }
                    __typename
                    }
                    __typename
                }
                __typename
                }
                __typename
            }
            ... on ImageAsset {
                media {
                id
                metadata {
                    id
                    contentAuthenticity {
                    credentials {
                        hasCredentials
                        inspectUrl
                        aiStatus
                        __typename
                    }
                    __typename
                    }
                    __typename
                }
                __typename
                }
                __typename
            }
            ... on DocumentAsset {
                media {
                id
                metadata {
                    id
                    contentAuthenticity {
                    credentials {
                        hasCredentials
                        inspectUrl
                        aiStatus
                        __typename
                    }
                    __typename
                    }
                    __typename
                }
                __typename
                }
                __typename
            }
            __typename
            }
        '''

        pdata = {'operationName': 'GetAssetsForViewer', 'variables': variables, 'query': self.gqlmin(query)}
        hdrs2 = hdrs.copy()
        hdrs2.update({
            'x-gql-op': 'GetAssetsForViewer',
            'x-frameio-share-authentication': helpers.b64encode(share_id),
            'apollographql-client-name': 'web-app',
            'apollographql-client-version': '@frameio/next-web-app@467.0'
        })
        data = self.net.http_POST(api_url, pdata, headers=hdrs2, jdata=True).content
        data = json.loads(data).get('data').get('assets')[0].get('media')
        return data.get('original', {}).get('downloadUrl') or data.get('hlsManifest')
