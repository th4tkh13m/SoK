/*
 * Copyright 2002-2016 the original author or authors.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package org.springframework.web.servlet;

import java.io.IOException;
import javax.servlet.RequestDispatcher;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.springframework.util.AntPathMatcher;
import org.springframework.util.PathMatcher;
import org.springframework.util.StringUtils;
import org.springframework.web.context.support.ServletContextResource;

/**
 * Simple servlet that can expose an internal resource, including a
 * default URL if the specified resource is not found. An alternative,
 * for example, to trying and catching exceptions when using JSP include.
 *
 * <p>A further usage of this servlet is the ability to apply last-modified
 * timestamps to quasi-static resources (typically JSPs). This can happen
 * as bridge to parameter-specified resources, or as proxy for a specific
 * target resource (or a list of specific target resources to combine).
 *
 * <p>A typical usage would map a URL like "/ResourceServlet" onto an instance
 * of this servlet, and use the "JSP include" action to include this URL,
 * with the "resource" parameter indicating the actual target path in the WAR.
 *
 * <p>The {@code defaultUrl} property can be set to the internal
 * resource path of a default URL, to be rendered when the target resource
 * is not found or not specified in the first place.
 *
 * <p>The "resource" parameter and the {@code defaultUrl} property can
 * also specify a list of target resources to combine. Those resources will be
 * included one by one to build the response. If last-modified determination
 * is active, the newest timestamp among those files will be used.
 *
 * <p>The {@code allowedResources} property can be set to a URL
 * pattern of resources that should be available via this servlet.
 * If not set, any target resource can be requested, including resources
 * in the WEB-INF directory!
 *
 * <p>If using this servlet for direct access rather than via includes,
 * the {@code contentType} property should be specified to apply a
 * proper content type. Note that a content type header in the target JSP will
 * be ignored when including the resource via a RequestDispatcher include.
 *
 * <p>To apply last-modified timestamps for the target resource, set the
 * {@code applyLastModified} property to true. This servlet will then
 * return the file timestamp of the target resource as last-modified value,
 * falling back to the startup time of this servlet if not retrievable.
 *
 * <p>Note that applying the last-modified timestamp in the above fashion
 * just makes sense if the target resource does not generate content that
 * depends on the HttpSession or cookies; it is just allowed to evaluate
 * request parameters.
 *
 * <p>A typical case for such last-modified usage is a JSP that just makes
 * minimal usage of basic means like includes or message resolution to
 * build quasi-static content. Regenerating such content on every request
 * is unnecessary; it can be cached as long as the file hasn't changed.
 *
 * <p>Note that this servlet will apply the last-modified timestamp if you
 * tell it to do so: It's your decision whether the content of the target
 * resource can be cached in such a fashion. Typical use cases are helper
 * resources that are not fronted by a controller, like JavaScript files
 * that are generated by a JSP (without depending on the HttpSession).
 *
 * @author Juergen Hoeller
 * @author Rod Johnson
 * @see #setDefaultUrl
 * @see #setAllowedResources
 * @see #setApplyLastModified
 * @deprecated as of Spring 4.3.5, in favor of
 * {@link org.springframework.web.servlet.resource.ResourceHttpRequestHandler}
 */
@SuppressWarnings("serial")
@Deprecated
public class ResourceServlet extends HttpServletBean {

	/**
	 * Any number of these characters are considered delimiters
	 * between multiple resource paths in a single String value.
	 */
	public static final String RESOURCE_URL_DELIMITERS = ",; \t\n";

	/**
	 * Name of the parameter that must contain the actual resource path.
	 */
	public static final String RESOURCE_PARAM_NAME = "resource";


	private String defaultUrl;

	private String allowedResources;

	private String contentType;

	private boolean applyLastModified = false;

	private PathMatcher pathMatcher;

	private long startupTime;


	/**
	 * Set the URL within the current web application from which to
	 * include content if the requested path isn't found, or if none
	 * is specified in the first place.
	 * <p>If specifying multiple URLs, they will be included one by one
	 * to build the response. If last-modified determination is active,
	 * the newest timestamp among those files will be used.
	 * @see #setApplyLastModified
	 */
	public void setDefaultUrl(String defaultUrl) {
		this.defaultUrl = defaultUrl;
	}

	/**
	 * Set allowed resources as URL pattern, e.g. "/WEB-INF/res/*.jsp",
	 * The parameter can be any Ant-style pattern parsable by AntPathMatcher.
	 * @see org.springframework.util.AntPathMatcher
	 */
	public void setAllowedResources(String allowedResources) {
		this.allowedResources = allowedResources;
	}

	/**
	 * Set the content type of the target resource (typically a JSP).
	 * Default is none, which is appropriate when including resources.
	 * <p>For directly accessing resources, for example to leverage this
	 * servlet's last-modified support, specify a content type here.
	 * Note that a content type header in the target JSP will be ignored
	 * when including the resource via a RequestDispatcher include.
	 */
	public void setContentType(String contentType) {
		this.contentType = contentType;
	}

	/**
	 * Set whether to apply the file timestamp of the target resource
	 * as last-modified value. Default is "false".
	 * <p>This is mainly intended for JSP targets that don't generate
	 * session-specific or database-driven content: Such files can be
	 * cached by the browser as long as the last-modified timestamp
	 * of the JSP file doesn't change.
	 * <p>This will only work correctly with expanded WAR files that
	 * allow access to the file timestamps. Else, the startup time
	 * of this servlet is returned.
	 */
	public void setApplyLastModified(boolean applyLastModified) {
		this.applyLastModified = applyLastModified;
	}


	/**
	 * Remember the startup time, using no last-modified time before it.
	 */
	@Override
	protected void initServletBean() {
		this.pathMatcher = getPathMatcher();
		this.startupTime = System.currentTimeMillis();
	}

	/**
	 * Return a {@link PathMatcher} to use for matching the "allowedResources" URL pattern.
	 * <p>The default is {@link AntPathMatcher}.
	 * @see #setAllowedResources
	 * @see org.springframework.util.AntPathMatcher
	 */
	protected PathMatcher getPathMatcher() {
		return new AntPathMatcher();
	}


	/**
	 * Determine the URL of the target resource and include it.
	 * @see #determineResourceUrl
	 */
	@Override
	protected final void doGet(HttpServletRequest request, HttpServletResponse response)
			throws ServletException, IOException {

		// Determine URL of resource to include...
		String resourceUrl = determineResourceUrl(request);

		if (resourceUrl != null) {
			try {
				doInclude(request, response, resourceUrl);
			}
			catch (ServletException ex) {
				if (logger.isWarnEnabled()) {
					logger.warn("Failed to include content of resource [" + resourceUrl + "]", ex);
				}
				// Try including default URL if appropriate.
				if (!includeDefaultUrl(request, response)) {
					throw ex;
				}
			}
			catch (IOException ex) {
				if (logger.isWarnEnabled()) {
					logger.warn("Failed to include content of resource [" + resourceUrl + "]", ex);
				}
				// Try including default URL if appropriate.
				if (!includeDefaultUrl(request, response)) {
					throw ex;
				}
			}
		}

		// No resource URL specified -> try to include default URL.
		else if (!includeDefaultUrl(request, response)) {
			throw new ServletException("No target resource URL found for request");
		}
	}

	/**
	 * Determine the URL of the target resource of this request.
	 * <p>Default implementation returns the value of the "resource" parameter.
	 * Can be overridden in subclasses.
	 * @param request current HTTP request
	 * @return the URL of the target resource, or {@code null} if none found
	 * @see #RESOURCE_PARAM_NAME
	 */
	protected String determineResourceUrl(HttpServletRequest request) {
		return request.getParameter(RESOURCE_PARAM_NAME);
	}

	/**
	 * Include the specified default URL, if appropriate.
	 * @param request current HTTP request
	 * @param response current HTTP response
	 * @return whether a default URL was included
	 * @throws ServletException if thrown by the RequestDispatcher
	 * @throws IOException if thrown by the RequestDispatcher
	 */
	private boolean includeDefaultUrl(HttpServletRequest request, HttpServletResponse response)
		throws ServletException, IOException {

		if (this.defaultUrl == null) {
			return false;
		}
		doInclude(request, response, this.defaultUrl);
		return true;
	}

	/**
	 * Include the specified resource via the RequestDispatcher.
	 * @param request current HTTP request
	 * @param response current HTTP response
	 * @param resourceUrl the URL of the target resource
	 * @throws ServletException if thrown by the RequestDispatcher
	 * @throws IOException if thrown by the RequestDispatcher
	 */
private void doInclude(HttpServletRequest request, HttpServletResponse response, String resourceUrl)
		throws ServletException, IOException {

		if (this.contentType != null) {
			response.setContentType(this.contentType);
		}

		if (logger.isDebugEnabled()) {
			logger.debug("Resource URLs: " + resourceUrl);
		}

		String[] resourceUrls = StringUtils.tokenizeToStringArray(resourceUrl, RESOURCE_URL_DELIMITERS);
		for (String url : resourceUrls) {
			// Check whether URL matches allowed resources
			if (this.allowedResources != null && !this.pathMatcher.match(this.allowedResources, url)) {
				throw new ServletException("Resource [" + url +
						"] does not match allowed pattern [" + this.allowedResources + "]");
			}
			if (logger.isDebugEnabled()) {
				logger.debug("Including resource [" + url + "]");
			}
			RequestDispatcher rd = request.getRequestDispatcher(url);
			rd.include(request, response);
		}
	}
	/**
	 * Return the last-modified timestamp of the file that corresponds
	 * to the target resource URL (i.e. typically the request ".jsp" file).
	 * Will simply return -1 if "applyLastModified" is false (the default).
	 * <p>Returns no last-modified date before the startup time of this servlet,
	 * to allow for message resolution etc that influences JSP contents,
	 * assuming that those background resources might have changed on restart.
	 * <p>Returns the startup time of this servlet if the file that corresponds
	 * to the target resource URL couldn't be resolved (for example, because
	 * the WAR is not expanded).
	 * @see #determineResourceUrl
	 * @see #getFileTimestamp
	 */
	@Override
	protected final long getLastModified(HttpServletRequest request) {
		if (this.applyLastModified) {
			String resourceUrl = determineResourceUrl(request);
			if (resourceUrl == null) {
				resourceUrl = this.defaultUrl;
			}
			if (resourceUrl != null) {
				String[] resourceUrls = StringUtils.tokenizeToStringArray(resourceUrl, RESOURCE_URL_DELIMITERS);
				long latestTimestamp = -1;
				for (String url : resourceUrls) {
					long timestamp = getFileTimestamp(url);
					if (timestamp > latestTimestamp) {
						latestTimestamp = timestamp;
					}
				}
				return (latestTimestamp > this.startupTime ? latestTimestamp : this.startupTime);
			}
		}
		return -1;
	}

	/**
	 * Return the file timestamp for the given resource.
	 * @param resourceUrl the URL of the resource
	 * @return the file timestamp in milliseconds, or -1 if not determinable
	 */
	protected long getFileTimestamp(String resourceUrl) {
		ServletContextResource resource = new ServletContextResource(getServletContext(), resourceUrl);
		try {
			long lastModifiedTime = resource.lastModified();
			if (logger.isDebugEnabled()) {
				logger.debug("Last-modified timestamp of " + resource + " is " + lastModifiedTime);
			}
			return lastModifiedTime;
		}
		catch (IOException ex) {
			if (logger.isWarnEnabled()) {
				logger.warn("Couldn't retrieve last-modified timestamp of " + resource +
						" - using ResourceServlet startup time");
			}
			return -1;
		}
	}

}
