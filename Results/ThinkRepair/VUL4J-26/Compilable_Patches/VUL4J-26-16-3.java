public String getUrlRegex() {
    if (StringUtils.isNotEmpty(urlRegex)) {
        return urlRegex;
    } else {
        return "^(https?|ftp):\\/\\/" +
                "(([a-z0-9_!~*'().&=+$%-]+: )?[a-z0-9_!~*'().&=+$%-]+@)?" +
                "(([0-9]{1,3}\\.){3}[0-9]{1,3}" +
                "|" +
                "([a-z0-9_!~*'()-]+\\.)*" +
                "([a-z]{2,})" +
                ")" +
                "(:[0-9]{1,5})?" +
                "(/([a-z0-9_!~*'().;?:@&=+$,%#-]|%[0-9a-f]{2})*)?" +
                "(\\?[a-z0-9_!~*'().;?:@&=+$,%#-]+)?" +
                "$";
    }
}