public String getForwardPage(HttpServletRequest request) {
    String pathInfo = request.getPathInfo();
    return (pathInfo != null) ? pathInfo : "defaultPage";
}