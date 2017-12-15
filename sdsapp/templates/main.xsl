<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="xml"
            media-type="text/xml"
            doctype-public="-//W3C//DTD XHTML 1.0 Transitional//EN"
            doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"
            indent="yes"
            omit-xml-declaration="yes"
            encoding="UTF-8" />

<xsl:template match="/">
<html lang="en" xml:lang="en">
  <head>
    <meta charset="utf-8"/>
    <meta http-equiv="X-UA-Compatible" content="IE=edge"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <meta name="description" content="pyramid web application"/>
    <meta name="author" content="Pylons Project"/>
    <link rel="shortcut icon" href="/static/pyramid-16x16.png"/>

    <title>Cookiecutter Starter project for the Pyramid Web Framework</title>

    <!-- Bootstrap core CSS -->
    <link href="//oss.maxcdn.com/libs/twitter-bootstrap/3.0.3/css/bootstrap.min.css" rel="stylesheet"/>

    <!-- Custom styles for this scaffold -->
    <link href="/static/theme.css" rel="stylesheet"/>

    <!-- HTML5 shim and Respond.js IE8 support of HTML5 elements and media queries -->
    <!--[if lt IE 9]>
      <script src="//oss.maxcdn.com/libs/html5shiv/3.7.0/html5shiv.js" integrity="sha384-0s5Pv64cNZJieYFkXYOTId2HMA2Lfb6q2nAcx2n0RTLUnCAoTTsS0nKEO27XyKcY" crossorigin="anonymous"></script>
      <script src="//oss.maxcdn.com/libs/respond.js/1.3.0/respond.min.js" integrity="sha384-f1r2UzjsxZ9T4V1f2zBO/evUqSEOpeaUUZcMTz1Up63bl4ruYnFYeM+BxI4NhyI0" crossorigin="anonymous"></script>
    <![endif]-->
  </head>

<body>
	<div class="header">
		<div class="container">
			<div class="logo">
				<a href="/">Catalog App</a>
			</div>
			<div class="log-btn">
				<xsl:choose>
					<xsl:when test="not(/root/@user)">
						<a id="login-btn">Login</a>
					</xsl:when>
					<xsl:otherwise>
						<a id="logout-btn" href="/logout">Logout <xsl:value-of select="/root/@user"/></a>
					</xsl:otherwise>
				</xsl:choose>
			</div>
		</div>
	</div>
	<div class="container">
        <div class="row">
<xsl:choose>
	<xsl:when test="/root/@view='top' or /root/@view='category'">
		<div class="col-md-2">
        	<xsl:call-template name="category-list">
        		<xsl:with-param name="src" select ="/root/categories"/>
        	</xsl:call-template>
    	</div>
    	<div class="col-md-10">
			<xsl:call-template name="article-list">
				<xsl:with-param name="src" select ="/root/articles"/>
				<xsl:with-param name="view" select="string(/root/@view)"/>
			</xsl:call-template>
        </div>
	</xsl:when>
	<xsl:when test="/root/@view='article' and /root/@action='show'">
		<div class="col-md-12">
			<xsl:call-template name="article-view">
				<xsl:with-param name="src" select ="/root/article"/>
			</xsl:call-template>
			<xsl:call-template name="article-actions">
				<xsl:with-param name="src" select ="/root/article"/>
			</xsl:call-template>
		</div>
	</xsl:when>
	<xsl:when test="/root/@view='article' and /root/@action='modify'">
		<div class="col-md-12">
			<xsl:call-template name="article-edit">
				<xsl:with-param name="src" select ="/root/article"/>
				<xsl:with-param name="title" select ="'Edit Item'"/>
			</xsl:call-template>
		</div>
	</xsl:when>
	<xsl:when test="/root/@view='article' and /root/@action='create'">
		<div class="col-md-12">
			<xsl:call-template name="article-edit">
				<xsl:with-param name="src" select ="/root/article"/>
				<xsl:with-param name="title" select ="'Add Item'"/>
			</xsl:call-template>
		</div>
	</xsl:when>
	<xsl:when test="/root/@view='article' and /root/@action='delete'">
		<div class="col-md-12">
			<xsl:call-template name="article-delete">
				<xsl:with-param name="src" select ="/root/article"/>
			</xsl:call-template>
		</div>
	</xsl:when>
</xsl:choose>
        </div>
	</div>


    <!-- Bootstrap core JavaScript
    ================================================== -->
    <!-- Placed at the end of the document so the pages load faster -->
    <script src="//oss.maxcdn.com/libs/jquery/1.10.2/jquery.min.js" integrity="sha384-aBL3Lzi6c9LNDGvpHkZrrm3ZVsIwohDD7CDozL0pk8FwCrfmV7H9w8j3L7ikEv6h" crossorigin="anonymous"></script>
    <script src="//oss.maxcdn.com/libs/twitter-bootstrap/3.0.3/js/bootstrap.min.js" integrity="sha384-s1ITto93iSMDxlp/79qhWHi+LsIi9Gx6yL+cOKDuymvihkfol83TYbLbOw+W/wv4" crossorigin="anonymous"></script>
    <xsl:call-template name="raw-xml-data"/>
    <xsl:if test="/root/@view='article' and /root/@action='create'">
    	<xsl:call-template name="desc-importer"/>
    </xsl:if>
    
    <xsl:if test="not(/root/@user)">
    	<xsl:call-template name="login-form"/>
    </xsl:if>
</body>
</html>

</xsl:template>

<xsl:template name="desc-importer">
	<script>
$(document).ready(function()
{
	$("#import-desc").click (function()
	{
		var self = $(this);
		var title = $("#aedit-form input[name=title]").val ();
		if (!title || (title=""))
			return false
		self.parent().find("div").remove ();
		$.ajax({
			type: "POST", 
			url: "/catalog/import_article",
			data: $("#aedit-form").serialize (),
			success: function (data){
				if (data.success)
				{
					var ndiv = self.parent().append('<div style="height:240px;overflow:scroll" class="form-control">'+data.html+'</div>');
				}
			}
		});
		return false;
	});
    
});
	</script>
</xsl:template>

<xsl:template name="article-delete">
	<xsl:param name="src"/>
	<div class="title">Delete Item</div>
	<form role="form" action="/catalog/{/root/category/@slug}/{$src/@slug}/delete" method="post" id="aedit-form">
		<input type="hidden" name="id" value="{$src/@id}"/>
		<div class="form-group">
			<div class="row">
				<div class="col-lg-12">
					<label class="col-lg-4 control-label">Are you sure you want to delete:</label>
				</div>
			</div>
		</div>
		<div class="form-group">
			<div class="col-lg-10"/>
			<div class="col-lg-2">
				<button type="submit" class="btn btn-primary" data-loading-text="Processing...">Submit</button>
			</div>
		</div>
	</form>
</xsl:template>


<xsl:template name="article-edit">
	<xsl:param name="src"/>
	<xsl:param name="title"/>
	<xsl:variable name="action">
		<xsl:choose>
			<xsl:when test="/root/@action='modify'">
				<xsl:value-if select="concat('/catalog/','/root/category/@slug', '/', $src/@slug, '/edit')"/>
			</xsl:when>
			<xsl:when test="/root/@action='create'">/catalog/new_article</xsl:when>
		</xsl:choose>
	</xsl:variable>
	<div class="title"><xsl:value-of select="$title"/></div>
	<form role="form" action="{$action}" method="post" id="aedit-form">
		<input type="hidden" name="id" value="{$src/@id}"/>
		<div class="form-group">
			<div class="row">
				<div class="col-lg-12">
					<label class="col-lg-4 control-label">Title:</label>
					<div class="col-lg-8">
						<input type="text" class="form-control" placeholder="Enter article title" name="title" maxlength="20" value="{$src/title}"/>
						<xsl:if test="$src/title/@error">
							<label class="error">
								<xsl:value-of select="$src/title/@error"/>
							</label>
						</xsl:if>
					</div>
				</div>
			</div>
			<div class="row">
				<div class="col-lg-12">
					<label class="col-lg-4 control-label">Description:</label>
					<div class="col-lg-8">
						<textarea type="password" class="form-control" placeholder="Enter article text" name="description" rows="12">
							<xsl:value-of select="$src/description"/>
						</textarea>
						<xsl:if test="/root/@action='create'">
							<button id="import-desc" class="btn btn-primary btn-xs" title="Try to import description from WIKI">WIKI</button>
						</xsl:if>
						<xsl:if test="$src/description/@error">
							<label class="error">
								<xsl:value-of select="$src/description/@error"/>
							</label>
						</xsl:if>
					</div>
				</div>
			</div>
			<div class="row">
				<div class="col-lg-12">
					<label class="col-lg-4 control-label">Category:</label>
					<div class="col-lg-8">
						<select class="form-control" name="categoryId">
							<xsl:for-each select="/root/categories/category">
								<option value="{@id}">
									<xsl:if test="$src/@categoryId=@id">
										<xsl:attribute name="selected">selected</xsl:attribute>
									</xsl:if>
									<xsl:value-of select="title"/>
								</option>
							</xsl:for-each>
						</select>
						<xsl:if test="$src/categoryId/@error">
							<label class="error">
								<xsl:value-of select="$src/categoryId/@error"/>
							</label>
						</xsl:if>
					</div>
				</div>
			</div>
		</div>
		<div class="form-group">
			<div class="col-lg-12">
				<xsl:choose>
					<xsl:when test="/root/error">
						<label class="error">
							<xsl:value-of select="/root/error"/>
						</label>
					</xsl:when>
					<xsl:otherwise><label class="error hidden"/></xsl:otherwise>
				</xsl:choose>
			</div>
		</div>
		<div class="form-group">
			<div class="col-lg-8"/>
			<div class="col-lg-2">
				<button type="submit" class="btn btn-primary">Submit</button>
			</div>
		</div>
	</form>
</xsl:template>

<xsl:template name="article-view">
	<xsl:param name="src"/>
	<div class="item-view">
		<div class="title">
			<xsl:value-of select="$src/title"/>
		</div>
		<div class="desc">
			<xsl:value-of select="$src/description"/>
		</div>
	</div>
</xsl:template>

<xsl:template name="article-actions">
	<xsl:param name="src"/>
	<div class="item-actions">
		<xsl:if test="/root/permissions/cpermission[@action='modify' and @item=$src/@id]">
			<a href="/catalog/{/root/category/@slug}/{$src/@slug}/edit">Edit</a>
		&#160;&#160;|&#160;&#160;
		</xsl:if>
		<xsl:if test="/root/permissions/cpermission[@action='delete' and @item=$src/@id]">
			<a href="/catalog/{/root/category/@slug}/{$src/@slug}/delete">Delete</a>
		</xsl:if>
	</div>
</xsl:template>

<xsl:template name="login-form">
<div aria-hidden="true" class="modal fade" role="dialog" id="login-popup">
	<div class="modal-dialog">
		<div class="modal-content">
			<div class="modal-body">
				<div class="row">
					<div class="col-lg-12">
						<form role="form" action="/login" method="post" id="login-form">
							<div class="form-group">
								<div class="row">
									<div class="col-lg-12">
										<label class="col-lg-4 control-label">Login:</label>
										<div class="col-lg-8">
											<input type="text" class="form-control" placeholder="Enter yours login" name="login" maxlength="20"/>
										</div>
									</div>
								</div>
								<div class="row">
									<div class="col-lg-12">
										<label class="col-lg-4 control-label">Password:</label>
										<div class="col-lg-8">
											<input type="password" class="form-control" placeholder="Enter yours password" name="password" maxlength="20"/>
										</div>
									</div>
								</div>
							</div>
							<div class="form-group">
								<div class="col-lg-12">
									<label class="error hidden">Error message</label>
								</div>
							</div>
							<div class="form-group">
								<div class="col-lg-8"/>
								<div class="col-lg-2">
									<button type="submit" class="btn btn-primary" data-loading-text="Processing...">Login</button>
								</div>
								<div class="col-lg-2">
									<button class="btn btn-default" data-dismiss="modal" type="button">Close</button>
								</div>
							</div>
						</form>
					</div>
				</div>
			</div>
		</div>
	</div>
</div>
<script>
$(document).ready(function()
{
	$("#login-btn").click (function()
	{
		$(".modal-backdrop").remove ();
		$("#login-popup").modal({backdrop:"static"});
	});
	$("#login-form").submit (function()
	{
		var self = $(this);
		$.ajax({
			type: "POST", 
			url: self.attr("action"),
			data: self.serialize (),
			success: function (data){
				if (data.success)
					document.location.reload ()
				else
				{
					self.find (".error").removeClass ("hidden");
					self.find (".error").text (data.error);
				}
			},
			error: function (){
				$("body").removeClass("modal-open");
				$(".modal-backdrop").remove ();
			}
		});
		return false;
	});
});
</script>
</xsl:template>

<xsl:template name="category-list">
	<xsl:param name="src"/>
	<div class="item-list left">
		<div class="title">Categories</div>
		<ul>
			<xsl:for-each select="$src/category">
				<xsl:sort select="@slug"/>
				<li><a href="/catalog/{@slug}/items"><xsl:value-of select="title"/></a></li>
			</xsl:for-each>
		</ul>
	</div>
</xsl:template>

<xsl:template name="article-list">
	<xsl:param name="src"/>
	<xsl:param name="view"/>
	<div class="item-list">
		<xsl:if test="/root/permissions/cpermission[@view='article' and @action='create']">
			<div class="item-actions">
				<a href="/catalog/new_article">Add Item</a>
			</div>
		</xsl:if>
		<div class="title">
			<xsl:choose>
				<xsl:when test="$view='category'">
					<xsl:variable name="cat-id" select="$src/@categoryId"/>
					<xsl:variable name="cat-data" select="/root/categories/category[@id=$cat-id]"/>
					<xsl:value-of select="$cat-data/title"/> Items (<xsl:value-of select="count ($src/article)"/> items)
				</xsl:when>
				<xsl:otherwise>Latest Items</xsl:otherwise>
			</xsl:choose>
		</div>
		<ul>
			<xsl:for-each select="$src/article">
				<xsl:sort select="position()" order="descending"/>
				<li>
					<xsl:variable name="cat-id" select="@categoryId"/>
					<xsl:variable name="cat-data" select="/root/categories/category[@id=$cat-id]"/>
					<a href="/catalog/{$cat-data/@slug}/{@slug}"><xsl:value-of select="title"/></a>
					<xsl:if test="$view='top'">
						<span>
							(<xsl:value-of select="$cat-data/title"/>)
						</span>
					</xsl:if>
				</li>
			</xsl:for-each>
		</ul>
	</div>
</xsl:template>

<!-- Raw XML received by view -->
<xsl:template name="raw-xml-data">
	<xsl:param name="src" select="/"/>
	<script>
$(document).ready(function()
{
	$(".xml-debug .toolbar").click (function()
	{
		$(".xml-debug textarea").toggleClass("hidden");
	});
    
});
	</script>
	<div class="xml-debug">
		<div class="toolbar glyphicon glyphicon-cog icon-muted" title="Toggle XML View"/>
		<textarea cols="80" rows="25" class="hidden">
			<xsl:copy-of select="$src"/>
		</textarea>
	</div>
</xsl:template>


</xsl:stylesheet>