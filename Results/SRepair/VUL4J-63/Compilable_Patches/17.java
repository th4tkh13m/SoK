/*
 * Copyright 2015-present Open Networking Foundation
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.onosproject.ovsdb.rfc.utils;

/**
 * Version utility class.
 */
public final class VersionUtil {

    /**
     * Constructs a VersionUtil object. Utility classes should not have a public
     * or default constructor, otherwise IDE will compile unsuccessfully. This
     * class should not be instantiated.
     */
    private VersionUtil() {
    }

    public static final String DEFAULT_VERSION_STRING = "0.0.0";
    private static final String FORMAT = "(\\d+)\\.(\\d+)\\.(\\d+)";

    /**
     * Match version by the format.
     * @param version the version String
     * @throws IllegalArgumentException this is an illegal argument exception
     */
    public static void versionMatch(String version) {
        if (!version.matches(FORMAT)) {
            throw new IllegalArgumentException("<" + version
                    + "> does not match format " + FORMAT);
        }
    }

    /**
     * Compare fromVersion and toVersion.
     * @param fromVersion the initial version
     * @param toVersion the end of the version
     * @return an int number
     */
    public static int versionCompare(String fromVersion, String toVersion) {
        if (fromVersion == null || toVersion == null) {
            return -1;
        }

        String[] fromArr = fromVersion.split("\\.");
        String[] toArr = toVersion.split("\\.");

        // Check if there are the same number of version components in both versions
        if (fromArr.length != 3 || toArr.length != 3) {
            return -1;
        }

        int fromFirst = Integer.parseInt(fromArr[0]);
        int fromMiddle = Integer.parseInt(fromArr[1]);
        int fromEnd = Integer.parseInt(fromArr[2]);
        int toFirst = Integer.parseInt(toArr[0]);
        int toMiddle = Integer.parseInt(toArr[1]);
        int toEnd = Integer.parseInt(toArr[2]);

        // Compare each component of the versions
        if (fromFirst != toFirst) {
            return fromFirst - toFirst;
        } else if (fromMiddle != toMiddle) {
            return fromMiddle - toMiddle;
        } else {
            return fromEnd - toEnd;
        }
    }}
