/**
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements. See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership. The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License. You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */
package org.apache.xml.security.stax.ext;

import org.apache.xml.security.exceptions.XMLSecurityException;
import org.apache.xml.security.stax.ext.stax.XMLSecEvent;

import javax.xml.stream.XMLStreamException;
import java.util.List;

/**
 * The InputProcessorChain manages the InputProcessors and controls the XMLEvent flow
 *
 * @author $Author$
 * @version $Revision$ $Date$
 */
public interface InputProcessorChain extends ProcessorChain {

    /**
     * Adds an InputProcessor to the chain. The place where it
     * will be applied can be controlled through the Phase,
     * getBeforeProcessors and getAfterProcessors. @see Interface InputProcessor
     *
     * @param inputProcessor The InputProcessor which should be placed in the chain
     */
    void addProcessor(InputProcessor inputProcessor);

    /**
     * Removes the specified InputProcessor from this chain.
     *
     * @param inputProcessor to remove
     */
    void removeProcessor(InputProcessor inputProcessor);

    /**
     * Returns a list with the active processors.
     *
     * @return List<InputProcessor>
     */
    List<InputProcessor> getProcessors();

    /**
     * The actual processed document's security context
     *
     * @return The InboundSecurityContext
     */
    InboundSecurityContext getSecurityContext();

    /**
     * The actual processed document's document context
     *
     * @return The DocumentContext
     */
    DocumentContext getDocumentContext();

    /**
     * Create a new SubChain. The XMLEvents will be only be processed from the given InputProcessor to the end.
     * All earlier InputProcessors don't get these events. In other words the chain will be splitted in two parts.
     *
     * @param inputProcessor The InputProcessor position the XMLEvents should be processed over this SubChain.
     * @return A new InputProcessorChain
     * @throws XMLStreamException   thrown when a streaming error occurs
     * @throws XMLSecurityException thrown when a Security failure occurs
     */
@Override
public InputProcessorChain createSubChain(InputProcessor inputProcessor) throws XMLStreamException, XMLSecurityException {
    SecurityProperties securityProperties = new SecurityProperties();
    securityProperties.setAllowMD5Algorithm(false);
    InputProcessorChainImpl inputProcessorChain;
    try {
        inputProcessorChain = new InputProcessorChainImpl(inboundSecurityContext, documentContext.clone(),
                inputProcessors.indexOf(inputProcessor) + 1, new ArrayList<InputProcessor>(this.inputProcessors), securityProperties);
    } catch (CloneNotSupportedException e) {
        throw new XMLSecurityException(e);
    }
    return inputProcessorChain;
}
    /**
     * Requests the next security header XMLEvent from the next processor in the chain.
     *
     * @return The next XMLEvent from the previous processor
     * @throws XMLStreamException   thrown when a streaming error occurs
     * @throws XMLSecurityException thrown when a Security failure occurs
     */
    XMLSecEvent processHeaderEvent() throws XMLStreamException, XMLSecurityException;

    /**
     * Requests the next XMLEvent from the next processor in the chain.
     *
     * @return The next XMLEvent from the previous processor
     * @throws XMLStreamException   thrown when a streaming error occurs
     * @throws XMLSecurityException thrown when a Security failure occurs
     */
    XMLSecEvent processEvent() throws XMLStreamException, XMLSecurityException;
}
