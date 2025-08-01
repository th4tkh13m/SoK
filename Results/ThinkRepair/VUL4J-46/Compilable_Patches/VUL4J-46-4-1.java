protected XmlFactory(ObjectCodec oc, int xpFeatures, int xgFeatures,
        XMLInputFactory xmlIn, XMLOutputFactory xmlOut,
        String nameForTextElem) {
    super(oc);
    _xmlParserFeatures = xpFeatures;
    _xmlGeneratorFeatures = xgFeatures;
    _cfgNameForTextElement = nameForTextElem;
    
    if (xmlIn == null) {
        xmlIn = XMLInputFactory.newInstance();
    }
    if (xmlOut == null) {
        xmlOut = XMLOutputFactory.newInstance();
    }
    
    _initFactories(xmlIn, xmlOut);
    _xmlInputFactory = xmlIn;
    _xmlOutputFactory = xmlOut;
}