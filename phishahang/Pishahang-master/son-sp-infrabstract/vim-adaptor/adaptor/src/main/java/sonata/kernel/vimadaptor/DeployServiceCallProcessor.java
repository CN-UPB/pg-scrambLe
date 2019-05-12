/*
 * Copyright (c) 2015 SONATA-NFV, UCL, NOKIA, NCSR Demokritos ALL RIGHTS RESERVED.
 * 
 * Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
 * in compliance with the License. You may obtain a copy of the License at
 * 
 * http://www.apache.org/licenses/LICENSE-2.0
 * 
 * Unless required by applicable law or agreed to in writing, software distributed under the License
 * is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
 * or implied. See the License for the specific language governing permissions and limitations under
 * the License.
 * 
 * Neither the name of the SONATA-NFV, UCL, NOKIA, NCSR Demokritos nor the names of its contributors
 * may be used to endorse or promote products derived from this software without specific prior
 * written permission.
 * 
 * This work has been performed in the framework of the SONATA project, funded by the European
 * Commission under Grant number 671517 through the Horizon 2020 and 5G-PPP programmes. The authors
 * would like to acknowledge the contributions of their colleagues of the SONATA partner consortium
 * (www.sonata-nfv.eu).
 *
 * @author Dario Valocchi (Ph.D.), UCL
 * 
 */

package sonata.kernel.vimadaptor;

import com.fasterxml.jackson.databind.ObjectMapper;

import org.slf4j.LoggerFactory;

import sonata.kernel.vimadaptor.commons.ServiceDeployPayload;
import sonata.kernel.vimadaptor.commons.SonataManifestMapper;
import sonata.kernel.vimadaptor.messaging.ServicePlatformMessage;
import sonata.kernel.vimadaptor.wrapper.ComputeWrapper;
import sonata.kernel.vimadaptor.wrapper.WrapperBay;
import sonata.kernel.vimadaptor.wrapper.WrapperStatusUpdate;

import java.util.Observable;

public class DeployServiceCallProcessor extends AbstractCallProcessor {

  private static final org.slf4j.Logger Logger =
      LoggerFactory.getLogger(DeployServiceCallProcessor.class);

  private ServiceDeployPayload data;

  /**
   * Create a CallProcessor to process a DeployService API call.
   * 
   * @param message the message to the API call.
   * @param sid the session ID of the API call.
   * @param mux the AdaptorMux to which send back responses.
   */
  public DeployServiceCallProcessor(ServicePlatformMessage message, String sid, AdaptorMux mux) {
    super(message, sid, mux);
  }

  @Override
  public boolean process(ServicePlatformMessage message) {

    Logger.warn("Received a DeployService call. This call is deprecated. Send back error");

    this.sendToMux(new ServicePlatformMessage(
        "{\"request_status\":\"ERROR\",\"message\":\"This function is deprecated\"}",
        "application/json", message.getReplyTo(), message.getSid(), null));
    return true;
  }

  @Override
  public void update(Observable arg0, Object arg1) {
    WrapperStatusUpdate update = (WrapperStatusUpdate) arg1;
    if (update.getSid().equals(this.getSid())) {
      Logger.info("Received an update from the wrapper...");
      if (update.getStatus().equals("SUCCESS")) {
        Logger.info("Deploy " + this.getSid() + " succeed");

        // Sending a hook to trigger the WIM adaptor
        Logger.info("Sending partial response to WIM adaptor...");
        ServicePlatformMessage response =
            new ServicePlatformMessage(update.getBody(), "application/x-yaml",
                "infrastructure.wan.configure", this.getSid(), this.getMessage().getReplyTo());
        this.sendToMux(response);
      } else if (update.getStatus().equals("ERROR")) {
        Logger.warn("Deploy " + this.getSid() + " error");
        Logger.warn("Pushing back error...");
        ServicePlatformMessage response = new ServicePlatformMessage(update.getBody(),
            "application/x-yaml", this.getMessage().getReplyTo(), this.getSid(), null);
        this.sendToMux(response);
      } else {
        Logger.info("Deploy " + this.getSid() + " - " + update.getStatus());
        Logger.info("Message " + update.getBody());
      }

      // TODO handle other update from the compute wrapper;
    }
  }

  @SuppressWarnings("unused")
  @Deprecated
  private void deprecatedUse(ServicePlatformMessage message) {
    boolean out = true;
    Logger.info("Call received...");
    // parse the payload to get Wrapper UUID and NSD/VNFD from the request body
    Logger.info("Parsing payload...");
    data = null;
    ObjectMapper mapper = SonataManifestMapper.getSonataMapper();
    // ObjectMapper mapper = new ObjectMapper(new YAMLFactory());
    // SimpleModule module = new SimpleModule();
    // module.addDeserializer(Unit.class, new UnitDeserializer());
    // //module.addDeserializer(VmFormat.class, new VmFormatDeserializer());
    // //module.addDeserializer(ConnectionPointType.class, new ConnectionPointTypeDeserializer());
    // mapper.registerModule(module);
    // mapper.enable(DeserializationFeature.READ_ENUMS_USING_TO_STRING);
    // mapper.disable(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES);
    try {
      data = mapper.readValue(message.getBody(), ServiceDeployPayload.class);
      Logger.info("payload parsed");
      ComputeWrapper wr = WrapperBay.getInstance().getComputeWrapper(data.getVimUuid());
      Logger.info("Wrapper retrieved");
      if (wr == null) {
        Logger.warn("Error retrieving the wrapper");

        this.sendToMux(new ServicePlatformMessage(
            "{\"request_status\":\"fail\",\"message\":\"VIM not found\"}", "application/json",
            message.getReplyTo(), message.getSid(), null));
        out = false;
      } else {
        // use wrapper interface to send the NSD/VNFD, along with meta-data
        // to the wrapper, triggering the service instantiation.
        Logger.info("Calling wrapper: " + wr);
        wr.addObserver(this);
        wr.deployService(data, this.getSid());
      }
    } catch (Exception e) {
      Logger.error("Error deploying the system: " + e.getMessage(), e);
      this.sendToMux(new ServicePlatformMessage(
          "{\"request_status\":\"fail\",\"message\":\"Deployment Error\"}", "application/json",
          message.getReplyTo(), message.getSid(), null));
      out = false;
    }
  }


}
