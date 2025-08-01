protected void extractFile(final File srcF, final File dir, final InputStream compressedInputStream,
                           final String entryName, final Date entryDate, final boolean isDirectory,
                           final Integer mode, String symlinkDestination)
    throws IOException, ArchiverException {
    final File f = new File(dir, entryName).getCanonicalFile();

    if (!FileUtils.isAncestor(dir, f)) {
        throw new ArchiverException("Entry path is outside of the target directory: " + entryName);
    }

    try {
        if (!isOverwrite() && f.exists() && (f.lastModified() >= entryDate.getTime())) {
            return;
        }

        // create intermediary directories - sometimes zip don't add them
        final File dirF = f.getParentFile();
        if (dirF != null) {
            dirF.mkdirs();
        }

        if (!StringUtils.isEmpty(symlinkDestination)) {
            SymlinkUtils.createSymbolicLink(f, new File(symlinkDestination));
        } else if (isDirectory) {
            f.mkdirs();
        } else {
            OutputStream out = null;
            try {
                out = new FileOutputStream(f);

                IOUtil.copy(compressedInputStream, out);
            } finally {
                IOUtil.close(out);
            }
        }

        f.setLastModified(entryDate.getTime());

        if (!isIgnorePermissions() && mode != null && !isDirectory) {
            ArchiveEntryUtils.chmod(f, mode);
        }
    } catch (final FileNotFoundException ex) {
        getLogger().warn("Unable to expand to file " + f.getPath());
        throw ex; // Rethrow the exception
    }
}