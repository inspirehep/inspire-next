<?xml version="1.0" encoding="UTF-8"?>
<!--
This file is part of INSPIRE.
Copyright (C) 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016

INSPIRE is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License as
published by the Free Software Foundation; either version 2 of the
License, or (at your option) any later version.

INSPIRE is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
-->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:OAI-PMH="http://www.openarchives.org/OAI/2.0/"
                xmlns:arXiv="http://arxiv.org/OAI/arXiv/"
                exclude-result-prefixes="OAI-PMH arXiv"
                version="1.0">
  <!-- Global variables -->

  <xsl:variable name="lcletters">abcdefghijklmnopqrstuvwxyz</xsl:variable>
  <xsl:variable name="ucletters">ABCDEFGHIJKLMNOPQRSTUVWXYZ</xsl:variable>

  <!-- ************ FUNCTIONS ************ -->

  <!-- FUNCTION  replace-string -->
  <xsl:template name="replace-string">
    <xsl:param name="text"/>
    <xsl:param name="from"/>
    <xsl:param name="to"/>
    <xsl:choose>
      <xsl:when test="contains($text, $from)">
        <xsl:variable name="before" select="substring-before($text, $from)"/>
        <xsl:variable name="after" select="substring-after($text, $from)"/>
        <xsl:variable name="prefix" select="concat($before, $to)"/>

        <xsl:value-of select="$before"/>
        <xsl:value-of select="$to"/>
        <xsl:call-template name="replace-string">
          <xsl:with-param name="text" select="$after"/>
          <xsl:with-param name="from" select="$from"/>
          <xsl:with-param name="to" select="$to"/>
        </xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="$text"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- FUNCTION   output-65017a-subfields -->
  <xsl:template name="output-65017a-subfields">
    <xsl:param name="list" />
    <xsl:variable name="newlist" select="concat(normalize-space($list), ' ')" />
    <xsl:variable name="first" select="substring-before($newlist, ' ')" />
    <xsl:variable name="remaining" select="substring-after($newlist, ' ')" />
    <xsl:if test="not($first='')">
      <datafield tag="650" ind1="1" ind2="7">
        <subfield code="a"><xsl:value-of select="$first" /></subfield>
        <subfield code="2">arXiv</subfield>
      </datafield>
      <!-- <xsl:variable name="kb" select="fn:format($first,'KB(arxiv-to-inspire-categories.kb,4)')"/> -->
      <!-- <xsl:if test="not($kb='')">
        <datafield tag="650" ind1="1" ind2="7">
          <subfield code="a"><xsl:value-of select="$kb" /></subfield>
          <subfield code="2">INSPIRE</subfield>
        </datafield>
       </xsl:if> -->
    </xsl:if>
    <xsl:if test="$remaining">
      <xsl:call-template name="output-65017a-subfields">
        <xsl:with-param name="list" select="$remaining" />
      </xsl:call-template>
    </xsl:if>
  </xsl:template>

  <!-- FUNCTION  last-word : returns last word of a string of words separated by spaces -->
  <xsl:template name="last-word">
    <xsl:param name="text"/>
    <xsl:choose>
      <xsl:when test="contains(normalize-space($text), ' ')">
        <xsl:variable name="after" select="substring-after( normalize-space($text), ' ') "/>
        <xsl:call-template name="last-word">
          <xsl:with-param name="text" select="$after"/>
        </xsl:call-template>
      </xsl:when>
      <xsl:when test="contains(normalize-space($text), '.')">
        <xsl:variable name="after" select="substring-after( normalize-space($text), '.') "/>
        <xsl:call-template name="last-word">
          <xsl:with-param name="text" select="$after"/>
        </xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="$text"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>


  <!-- FUNCTION  rn-extract : returns a subfield for each reportnumber in a string (comma separted)  -->
  <xsl:template name="rn-extract">
    <xsl:param name="text"/>
    <xsl:choose>
      <xsl:when test="contains(normalize-space($text), ',')">
        <xsl:variable name="after" select="substring-after( normalize-space($text), ',')"/>
        <datafield tag="037" ind1=" " ind2=" ">
          <subfield code="a"><xsl:value-of select="substring-before( normalize-space($text), ',')"/></subfield>
        </datafield>
        <xsl:call-template name="rn-extract">
          <xsl:with-param name="text" select="$after"/>
        </xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
        <datafield tag="037" ind1=" " ind2=" ">
          <subfield code="a"><xsl:value-of select="$text"/></subfield>
        </datafield>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>


  <!-- FUNCTION Print sets values separated by ;  -->
  <xsl:template name="print-sets">
    <xsl:for-each select="./OAI-PMH:header/OAI-PMH:setSpec"><xsl:value-of select="."/>;</xsl:for-each>
  </xsl:template>


  <!-- Functions for author / collaboration extraction-->
  <xsl:template name="extractAuthor">
    <xsl:param name="node"/>
    <subfield code="a">
      <xsl:variable name="num-dots">
        <xsl:value-of select="string-length($node/arXiv:forenames) - string-length(translate($node/arXiv:forenames,'.',''))"/>
      </xsl:variable>
      <xsl:choose>
        <!-- Remove spaces if forename is only initials -->
        <xsl:when test="$num-dots &gt; 1 and string-length(translate(normalize-space($node/arXiv:forenames), ' ', '')) = ($num-dots*2)">
          <xsl:variable name="fnames">
      <xsl:value-of select="translate(normalize-space($node/arXiv:forenames), ' ', '')"/>
    </xsl:variable>
    <xsl:value-of select="$node/arXiv:keyname"/>, <xsl:value-of select="$fnames" />
        </xsl:when>
        <xsl:when test="not(contains($node/arXiv:forenames, 'Collaboration:')) and not(contains($node/arXiv:forenames, 'Consortium:'))">
    <xsl:variable name="fnames">
      <xsl:value-of select="normalize-space($node/arXiv:forenames)"/>
    </xsl:variable>
    <xsl:value-of select="$node/arXiv:keyname"/>, <xsl:value-of select="$fnames" />
        </xsl:when>
        <xsl:when test="contains($node/arXiv:forenames, 'Collaboration:')">
    <xsl:variable name="fnames">
      <xsl:value-of select="normalize-space(substring-after($node/arXiv:forenames, 'Collaboration:'))"/>
    </xsl:variable>
    <xsl:value-of select="$node/arXiv:keyname"/>, <xsl:value-of select="$fnames" />
        </xsl:when>
        <xsl:when test="contains($node/arXiv:forenames, 'Consortium:')">
    <xsl:variable name="fnames">
      <xsl:value-of select="normalize-space(substring-after($node/arXiv:forenames, 'Consortium:'))"/>
    </xsl:variable>
    <xsl:value-of select="$node/arXiv:keyname"/>, <xsl:value-of select="$fnames" />
        </xsl:when>
      </xsl:choose>
    </subfield>

    <xsl:for-each select="$node/arXiv:affiliation">
      <xsl:variable name="knlow"><xsl:value-of select="normalize-space(translate(., $ucletters, $lcletters))"/></xsl:variable>
      <xsl:if test="not (contains($knlow,'collab') or contains($knlow,'team') or contains($knlow,'group') or contains($knlow, 'for the'))">
        <subfield code="v"><xsl:value-of select="."/></subfield>
      </xsl:if>
    </xsl:for-each>
  </xsl:template>

  <xsl:template name="extractCollaborationSimple">
    <xsl:param name="node"/>
    <!-- Extracting collaboration from the simple author field
   ( containing only collaboration ) -->
    <xsl:variable name="knlowc" select="normalize-space(translate($node/arXiv:affiliation, $ucletters, $lcletters))" />
    <xsl:variable name="knlowfn" select="normalize-space(translate($node/arXiv:forenames, $ucletters, $lcletters))" />
    <xsl:variable name="knlowkn" select="normalize-space(translate($node/arXiv:keyname, $ucletters, $lcletters))" />
    <xsl:variable name="knlow" select="concat($knlowc,$knlowfn,$knlowkn)" />

    <xsl:if test="contains($knlow, 'collab') or contains($knlow, 'team') or contains($knlow,'group') or contains($knlow, 'for the') ">

      <xsl:choose>
        <xsl:when test="contains($knlowc, 'collab') or contains($knlowc, 'team') or contains($knlowc,'group') or contains($knlowc, 'for the')">
    <xsl:value-of select="$node/arXiv:affiliation"/>
        </xsl:when>
        <xsl:when test="contains($knlowfn, 'collab') or contains($knlowfn, 'team') or contains($knlowfn,'group') or contains($knlowfn, 'for the')">
    <xsl:value-of select="concat($node/arXiv:keyname , ' ', $node/arXiv:forenames)"/>
        </xsl:when>
        <xsl:when test="contains($knlowkn, 'collab') or contains($knlowkn, 'team') or contains($knlowkn, 'for the')">
    <xsl:value-of select="concat($node/arXiv:forenames, ' ', $node/arXiv:keyname)"/>
        </xsl:when>
        <xsl:otherwise>
    <xsl:value-of select="concat($node/arXiv:forenames, ' ', $node/arXiv:keyname, ' ', $node/arXiv:affiliation)"/>
        </xsl:otherwise>
      </xsl:choose>

    </xsl:if>
  </xsl:template>

  <xsl:template name="extractCollaborationComplex">
    <xsl:param name="node"/>
    <!-- Extracting collaboration in case when the same field contains
   collaboration and author information -->
    <xsl:choose>
      <xsl:when test="contains($node/arXiv:forenames, 'Consortium')">
        <xsl:value-of select="concat(substring-before($node/arXiv:forenames,'Consortium:'), ' consortium')"/>
      </xsl:when>
      <xsl:when test="contains($node/arXiv:forenames, 'Collaboration')">
        <xsl:value-of select="concat(substring-before($node/arXiv:forenames,'Collaboration:'), ' collaboration')"/>
      </xsl:when>
    </xsl:choose>
  </xsl:template>

  <xsl:template name="extractCollaboration">
    <xsl:param name="node"/>
    <datafield tag="710" ind1=" " ind2=" ">
      <subfield code="g">
        <xsl:choose>
    <xsl:when test="contains($node/arXiv:forenames, 'Collaboration:') or contains($node/arXiv:forenames, 'Consortium:')">
      <xsl:call-template name="extractCollaborationComplex">
        <xsl:with-param name="node" select="$node"/>
      </xsl:call-template>
    </xsl:when>
    <xsl:otherwise>
      <xsl:call-template name="extractCollaborationSimple">
        <xsl:with-param name="node" select="$node"/>
      </xsl:call-template>
    </xsl:otherwise>
        </xsl:choose>
      </subfield>
    </datafield>
  </xsl:template>

  <xsl:template name="firstAuthor">
    <xsl:param name="firstNode"/>
    <datafield tag="100" ind1=" " ind2=" ">
      <xsl:call-template name="extractAuthor">
        <xsl:with-param name="node" select="$firstNode"/>
      </xsl:call-template>
    </datafield>
  </xsl:template>

  <xsl:template name="furtherAuthor">
    <xsl:param name="node"/>
    <datafield tag="700" ind1=" " ind2=" ">
      <xsl:call-template name="extractAuthor">
        <xsl:with-param name="node" select="$node"/>
      </xsl:call-template>
    </datafield>
  </xsl:template>

  <xsl:template name="collaboration">
    <xsl:param name="node"/>
    <xsl:call-template name="extractCollaboration">
      <xsl:with-param name="node" select="$node"/>
    </xsl:call-template>
  </xsl:template>




  <!-- ************ MAIN CODE ************ -->

  <xsl:template match="/">
    <collection>
      <xsl:for-each select="//OAI-PMH:record">

        <!-- *** GLOBAL RECORD VARS *** -->

        <!-- Preparing base determination : getting category -->
        <xsl:variable name="setspec2">
          <xsl:value-of select="substring-after(./OAI-PMH:header/OAI-PMH:setSpec,':')"/>
        </xsl:variable>

        <!-- Preparing base determination : getting category -->
        <xsl:variable name="setspec">
          <xsl:call-template name="print-sets" />
        </xsl:variable>

        <!-- Getting category -->
        <xsl:variable name="category">
          <xsl:value-of select="./OAI-PMH:metadata/arXiv:arXiv/arXiv:categories"/>
        </xsl:variable>

        <!-- Preparing data : is this a thesis ? (we can find this in the abstract)-->
        <xsl:variable name="commentslow">
          <xsl:value-of select="translate(./OAI-PMH:metadata/arXiv:arXiv/arXiv:comments,$ucletters,$lcletters)"/>
        </xsl:variable>

        <xsl:variable name="lkrmatch">
          <xsl:value-of select="normalize-space(translate(./OAI-PMH:metadata/arXiv:arXiv/arXiv:comments, $ucletters, $lcletters))"/>
        </xsl:variable>

        <xsl:variable name="detectPR">accepted@appear@press@publ@review@submitted></xsl:variable>

        <!-- *** END GLOBAL RECIRD VARS *** -->

        <!-- *** START OUTPUT *** -->

        <xsl:choose>
          <!-- HANDLING DELETED RECORDS -->
          <xsl:when test="OAI-PMH:header[@status='deleted']">
            <record>
              <xsl:if test="./OAI-PMH:header/OAI-PMH:identifier | ./OAI-PMH:header/OAI-PMH:setSpec">
                <datafield tag="909" ind1="C" ind2="O">
                  <subfield code="o"><xsl:value-of select="./OAI-PMH:header/OAI-PMH:identifier"/></subfield>
                  <subfield code="p"><xsl:value-of select="./OAI-PMH:header/OAI-PMH:setSpec"/></subfield>
                </datafield>
              </xsl:if>
              <datafield tag="980" ind1="" ind2="">
                <subfield code="c">DELETED</subfield>
              </datafield>
            </record>
          </xsl:when>
          <!-- HANDLING NON-DELETED RECORDS -->
          <xsl:otherwise>
            <record>
              <!-- MARC FIELD 0247_$$2,a  = metadata/arXiv/doi  -->
              <xsl:if test="./OAI-PMH:metadata/arXiv:arXiv/arXiv:doi">
                <datafield tag="024" ind1="7" ind2=" ">
                  <subfield code="2">DOI</subfield>
                  <subfield code="a"><xsl:value-of select="./OAI-PMH:metadata/arXiv:arXiv/arXiv:doi"/></subfield>
                </datafield>
              </xsl:if>
              <!-- MARC FIELD 035_$$9,a  = metadata/header/identifier  -->
              <xsl:if test="./OAI-PMH:header/OAI-PMH:identifier">
                <datafield tag="035" ind1=" " ind2=" ">
                  <subfield code="9">arXiv</subfield>
                  <subfield code="a"><xsl:value-of select="./OAI-PMH:header/OAI-PMH:identifier"/></subfield>
                </datafield>
              </xsl:if>
              <!-- MARC FIELD 037_$$9,a,c = metadata/header/identifier  -->
              <xsl:if test="./OAI-PMH:header/OAI-PMH:identifier">
                <datafield tag="037" ind1=" " ind2=" ">
                  <subfield code="9">arXiv</subfield>
                  <subfield code="a">
                    <xsl:choose>
                      <xsl:when test="contains(./OAI-PMH:header/OAI-PMH:identifier, '/')">
                        <xsl:value-of select="substring-after(substring-after(./OAI-PMH:header/OAI-PMH:identifier, ':'), ':')" />
                      </xsl:when>
                      <xsl:otherwise>
                        <xsl:text>arXiv:</xsl:text><xsl:value-of select="substring-after(substring-after(./OAI-PMH:header/OAI-PMH:identifier, ':'), ':')" />
                      </xsl:otherwise>
                    </xsl:choose>
                  </subfield>
                  <xsl:if test="./OAI-PMH:metadata/arXiv:arXiv/arXiv:categories">
                    <subfield code="c">
                      <xsl:value-of select="substring-before(concat(./OAI-PMH:metadata/arXiv:arXiv/arXiv:categories, ' '), ' ')" />
                    </subfield>
                  </xsl:if>
                </datafield>
              </xsl:if>
              <!-- MARC FIELD 037_$$a = metadata/arXiv/report-no   -->
              <xsl:if test="./OAI-PMH:metadata/arXiv:arXiv/arXiv:report-no">
                <xsl:variable name="RN0">
                  <xsl:value-of select="translate(./OAI-PMH:metadata/arXiv:arXiv/arXiv:report-no, $lcletters, $ucletters)"/>
                </xsl:variable>
                <xsl:variable name="RN1">
                  <xsl:call-template name="replace-string">
                      <xsl:with-param name="text" select="$RN0"/>
                      <xsl:with-param name="from" select="'/'"/>
                      <xsl:with-param name="to" select="'-'"/>
                  </xsl:call-template>
                </xsl:variable>
                <xsl:variable name="RN2">
                  <xsl:call-template name="replace-string">
                    <xsl:with-param name="text" select="$RN1"/>
                    <xsl:with-param name="from" select="';'"/>
                    <xsl:with-param name="to" select="','"/>
                  </xsl:call-template>
                </xsl:variable>
                <xsl:variable name="RN3">
                  <xsl:call-template name="replace-string">
                    <xsl:with-param name="text" select="$RN2"/>
                    <xsl:with-param name="from" select="', '"/>
                    <xsl:with-param name="to" select="','"/>
                  </xsl:call-template>
                </xsl:variable>
                <xsl:variable name="RN4">
                  <xsl:call-template name="replace-string">
                    <xsl:with-param name="text" select="$RN3"/>
                    <xsl:with-param name="from" select="' '"/>
                    <xsl:with-param name="to" select="'-'"/>
                  </xsl:call-template>
                </xsl:variable>
                <xsl:call-template name="rn-extract">
                  <xsl:with-param name="text" select="$RN4"/>
                </xsl:call-template>
              </xsl:if>

              <!-- MARC FIELDS [1,7]00$$a,u  = metadata/arXiv/[author,affiliation]
                   N.B.: $$v not used, all affiliations are repeated in $$u -->

              <xsl:if test="./OAI-PMH:metadata/arXiv:arXiv/arXiv:authors/arXiv:author">
          <xsl:variable name="containingCollaboration" select="./OAI-PMH:metadata/arXiv:arXiv/arXiv:authors/arXiv:author[
                                                                     contains(translate(./arXiv:forenames, $lcletters, $ucletters), 'CONSORTIUM')
                                                                     or contains(translate(./arXiv:keyname, $lcletters, $ucletters) , 'CONSORTIUM')
                                                                     or contains(translate(./arXiv:affiliation, $lcletters, $ucletters) , 'CONSORTIUM')
                                                                     or contains(translate(./arXiv:forenames, $lcletters, $ucletters), 'COLLAB')
                                                                     or contains(translate(./arXiv:keyname, $lcletters, $ucletters) , 'COLLAB')
                                                                     or contains(translate(./arXiv:affiliation, $lcletters, $ucletters) , 'COLLAB')
                                                                     or contains(translate(./arXiv:forenames, $lcletters, $ucletters), 'TEAM')
                                                                     or contains(translate(./arXiv:keyname, $lcletters, $ucletters) , 'TEAM')
                                                                     or contains(translate(./arXiv:affiliation, $lcletters, $ucletters) , 'TEAM')
                                                                     or contains(translate(./arXiv:forenames, $lcletters, $ucletters), 'GROUP')
                                                                     or contains(translate(./arXiv:affiliation, $lcletters, $ucletters) , 'GROUP')
                                                                     or contains(translate(./arXiv:forenames, $lcletters, $ucletters), 'FOR THE')
                                                                     or contains(translate(./arXiv:keyname, $lcletters, $ucletters) , 'FOR THE')
                                                                     or contains(translate(./arXiv:affiliation, $lcletters, $ucletters) , 'FOR THE')
                                                                     ]"/>
          <xsl:variable name="containingAuthor" select="./OAI-PMH:metadata/arXiv:arXiv/arXiv:authors/arXiv:author[not(
                                                              contains(translate(./arXiv:forenames, $lcletters, $ucletters), 'CONSORTIUM')
                                                              or contains(translate(./arXiv:keyname, $lcletters, $ucletters) , 'CONSORTIUM')
                                                              or contains(translate(./arXiv:forenames, $lcletters, $ucletters), 'COLLAB')
                                                              or contains(translate(./arXiv:keyname, $lcletters, $ucletters) , 'COLLAB')
                                                              or contains(translate(./arXiv:forenames, $lcletters, $ucletters), 'TEAM')
                                                              or contains(translate(./arXiv:keyname, $lcletters, $ucletters) , 'TEAM')
                                                              or contains(translate(./arXiv:forenames, $lcletters, $ucletters), 'GROUP')
                                                              or contains(translate(./arXiv:forenames, $lcletters, $ucletters), 'FOR THE')
                                                              or contains(translate(./arXiv:keyname, $lcletters, $ucletters) , 'FOR THE')
                                                              )
                                                              or contains(./arXiv:forenames, 'Collaboration:')
                                                              or contains(./arXiv:forenames, 'Consortium:')]"/>

          <xsl:if test="$containingAuthor != ''">
                  <xsl:call-template name="firstAuthor">
              <xsl:with-param name="firstNode" select="$containingAuthor[1]"/>
            </xsl:call-template>
            <xsl:for-each select="$containingAuthor[position() > 1]">
              <xsl:call-template name="furtherAuthor">
                <xsl:with-param name="node" select="."/>
              </xsl:call-template>
            </xsl:for-each>
                </xsl:if>

                <xsl:if test="$containingCollaboration != ''">
            <xsl:for-each select="$containingCollaboration">
              <xsl:call-template name="collaboration">
                <xsl:with-param name="node" select="."/>
              </xsl:call-template>
            </xsl:for-each>
                </xsl:if>

              </xsl:if>

              <!-- MARC FIELD 245$$a = metadata/arXiv/title -->
              <xsl:if test="./OAI-PMH:metadata/arXiv:arXiv/arXiv:title">
                <datafield tag="245" ind1=" " ind2=" ">
                  <subfield code="a"><xsl:value-of select="normalize-space(./OAI-PMH:metadata/arXiv:arXiv/arXiv:title)"/></subfield>
                  <subfield code="9">arXiv</subfield>
                </datafield>
              </xsl:if>

              <!-- MARC FIELD  269$$c / date  -->
              <xsl:if test="./OAI-PMH:metadata/arXiv:arXiv/arXiv:created">
                <xsl:variable name="datebase" select="./OAI-PMH:metadata/arXiv:arXiv/arXiv:created"/>
                <xsl:variable name="year" select="substring-before($datebase,'-')"/>
                <xsl:variable name="month" select="substring-before(substring-after($datebase,'-'),'-')"/>
                <xsl:variable name="day" select="substring-after(substring-after($datebase,'-'),'-')"/>
                <datafield tag="269" ind1=" " ind2=" ">
                  <subfield code="c">
                    <xsl:value-of select="$year" />-<xsl:value-of select="$month" />-<xsl:value-of select="$day" />
                  </subfield>
                </datafield>
              </xsl:if>

              <!-- MARC FIELD 300$$a / pagination -->
              <xsl:if test="./OAI-PMH:metadata/arXiv:arXiv/arXiv:comments">
                <xsl:if test="contains(./OAI-PMH:metadata/arXiv:arXiv/arXiv:comments, 'pages')">
                  <xsl:variable name="beforepages">
                    <xsl:value-of select="normalize-space(substring-before(./OAI-PMH:metadata/arXiv:arXiv/arXiv:comments,'pages'))"/>
                  </xsl:variable>
                  <datafield tag="300" ind1=" " ind2=" ">
                    <subfield code="a"><xsl:call-template name="last-word"><xsl:with-param name="text" select="$beforepages"/></xsl:call-template></subfield>
                  </datafield>
                </xsl:if>
              </xsl:if>

              <!-- MARC FIELD 500$$a  = comments -->
              <xsl:if test="./OAI-PMH:metadata/arXiv:arXiv/arXiv:comments">
                <datafield tag="500" ind1=" " ind2=" ">
                  <subfield code="a">
                    <xsl:value-of select="normalize-space(./OAI-PMH:metadata/arXiv:arXiv/arXiv:comments)"/>
                  </subfield>
                  <subfield code="9">arXiv</subfield>
                </datafield>
              </xsl:if>

              <!-- MARC FIELD 500$$a  = Temp/Brief entry -->
              <xsl:choose>
                <xsl:when test="contains(./OAI-PMH:metadata/arXiv:arXiv/arXiv:categories, 'hep-')">
                  <datafield tag="500" ind1=" " ind2=" ">
                    <subfield code="a">*Temporary entry*</subfield>
                  </datafield>
                </xsl:when>
                <xsl:otherwise>
                  <datafield tag="500" ind1=" " ind2=" ">
                    <subfield code="a">*Brief entry*</subfield>
                  </datafield>
                </xsl:otherwise>
              </xsl:choose>

              <!-- MARC FIELD 520$$a  = metadata/arXiv/abstract -->
              <xsl:if test="./OAI-PMH:metadata/arXiv:arXiv/arXiv:abstract">
                <datafield tag="520" ind1=" " ind2=" ">
                  <subfield code="a">
                    <xsl:value-of select="normalize-space(./OAI-PMH:metadata/arXiv:arXiv/arXiv:abstract)"/>
                  </subfield>
                  <subfield code="9">arXiv</subfield>
                </datafield>
              </xsl:if>

              <!-- MARC FIELD 540$$a  License info = metadata/arXiv/license -->
              <xsl:if test="./OAI-PMH:metadata/arXiv:arXiv/arXiv:license">
                <datafield tag="540" ind1=" " ind2=" ">
                  <subfield code="u">
                    <xsl:value-of select="normalize-space(./OAI-PMH:metadata/arXiv:arXiv/arXiv:license)"/>
                  </subfield>
                  <subfield code="b">arXiv</subfield>
                  <xsl:choose>
                    <xsl:when test="contains(./OAI-PMH:metadata/arXiv:arXiv/arXiv:license, 'creativecommons.org/licenses/by/3.0')">
                      <subfield code="a">CC-BY-3.0</subfield>
                    </xsl:when>
                    <xsl:when test="contains(./OAI-PMH:metadata/arXiv:arXiv/arXiv:license, 'creativecommons.org/licenses/by-nc-sa/3.0')">
                      <subfield code="a">CC-BY-NC-SA-3.0</subfield>
                    </xsl:when>
                  </xsl:choose>
                </datafield>
              </xsl:if>

              <!-- MARC FIELD 65017$$ab = metadata/arXiv/categories -->
              <xsl:if test="./OAI-PMH:metadata/arXiv:arXiv/arXiv:categories">
                <xsl:call-template name="output-65017a-subfields">
                  <xsl:with-param name="list"><xsl:value-of select="./OAI-PMH:metadata/arXiv:arXiv/arXiv:categories"/></xsl:with-param>
                </xsl:call-template>
              </xsl:if>

              <!-- MARC FIELD 773 - using journal-ref field, journal extraction done in the filter now-->
              <xsl:if test="./OAI-PMH:metadata/arXiv:arXiv/arXiv:journal-ref">
                <datafield tag="773" ind1=" " ind2=" ">
                  <subfield code="x"><xsl:value-of select="./OAI-PMH:metadata/arXiv:arXiv/arXiv:journal-ref"/></subfield>
                </datafield>

              </xsl:if>

              <xsl:choose>
                <!-- Is this a thesis?  -->
                <xsl:when test="contains($commentslow,' diploma ') or contains($commentslow,' diplomarbeit ') or contains($commentslow,' diplome ') or contains($commentslow,' dissertation ') or contains($commentslow,' doctoraal ') or contains($commentslow,' doctoral ') or contains($commentslow,' doctorat ') or contains($commentslow,' doctorate ') or contains($commentslow,' doktorarbeit ') or contains($commentslow,' dottorato ') or contains($commentslow,' habilitationsschrift ') or contains($commentslow,' hochschule ') or contains($commentslow,' inauguraldissertation ') or contains($commentslow,' memoire ') or contains($commentslow,' phd ') or contains($commentslow,' proefschrift ') or contains($commentslow,' schlussbericht ') or contains($commentslow,' staatsexamensarbeit ') or contains($commentslow,' tesi ') or contains($commentslow,' thesis ') or contains($commentslow,' travail ') or contains($commentslow,' diploma,') or contains($commentslow,' diplomarbeit,') or contains($commentslow,' diplome,') or contains($commentslow,' dissertation,') or contains($commentslow,' doctoraal,') or contains($commentslow,' doctoral,') or contains($commentslow,' doctorat,') or contains($commentslow,' doctorate,') or contains($commentslow,' doktorarbeit,') or contains($commentslow,' dottorato,') or contains($commentslow,' habilitationsschrift,') or contains($commentslow,' hochschule,') or contains($commentslow,' inauguraldissertation,') or contains($commentslow,' memoire,') or contains($commentslow,' phd,') or contains($commentslow,' proefschrift,') or contains($commentslow,' schlussbericht,') or contains($commentslow,' staatsexamensarbeit,') or contains($commentslow,' tesi,') or contains($commentslow,' thesis,') or contains($commentslow,' travail,') or contains($commentslow,' diploma.') or contains($commentslow,' diplomarbeit.') or contains($commentslow,' diplome.') or contains($commentslow,' dissertation.') or contains($commentslow,' doctoraal.') or contains($commentslow,' doctoral.') or contains($commentslow,' doctorat.') or contains($commentslow,' doctorate.') or contains($commentslow,' doktorarbeit.') or contains($commentslow,' dottorato.') or contains($commentslow,' habilitationsschrift.') or contains($commentslow,' hochschule.') or contains($commentslow,' inauguraldissertation.') or contains($commentslow,' memoire.') or contains($commentslow,' phd.') or contains($commentslow,' proefschrift.') or contains($commentslow,' schlussbericht.') or contains($commentslow,' staatsexamensarbeit.') or contains($commentslow,' tesi.') or contains($commentslow,' thesis.') or contains($commentslow,' travail.') or contains($commentslow,' diploma;') or contains($commentslow,' diplomarbeit;') or contains($commentslow,' diplome;') or contains($commentslow,' dissertation;') or contains($commentslow,' doctoraal;') or contains($commentslow,' doctoral;') or contains($commentslow,' doctorat;') or contains($commentslow,' doctorate;') or contains($commentslow,' doktorarbeit;') or contains($commentslow,' dottorato;') or contains($commentslow,' habilitationsschrift;') or contains($commentslow,' hochschule;') or contains($commentslow,' inauguraldissertation;') or contains($commentslow,' memoire;') or contains($commentslow,' phd;') or contains($commentslow,' proefschrift;') or contains($commentslow,' schlussbericht;') or contains($commentslow,' staatsexamensarbeit;') or contains($commentslow,' tesi;') or contains($commentslow,' thesis;') or contains($commentslow,' travail;')">

                  <datafield tag="980" ind1=" " ind2=" ">
                    <subfield code="a">Thesis</subfield>
                  </datafield>

                </xsl:when>

                <!-- or Is this a conference?  -->
                <xsl:when test="contains($lkrmatch,' colloquium ') or
                                contains($lkrmatch,' colloquiums ') or
                                contains($lkrmatch,' conf ') or
                                contains($lkrmatch,' conference ') or
                                contains($lkrmatch,' conferences ') or
                                contains($lkrmatch,' contrib ') or
                                contains($lkrmatch,' contributed ') or
                                contains($lkrmatch,' contribution ') or
                                contains($lkrmatch,' contributions ') or
                                contains($lkrmatch,' forum ') or
                                contains($lkrmatch,' lecture ') or
                                contains($lkrmatch,' lectures ') or
                                contains($lkrmatch,' meeting ') or
                                contains($lkrmatch,' meetings ') or
                                contains($lkrmatch,' pres ') or
                                contains($lkrmatch,' presented ') or
                                contains($lkrmatch,' proc ') or
                                contains($lkrmatch,' proceeding ') or
                                contains($lkrmatch,' proceedings ') or
                                contains($lkrmatch,' rencontre ') or
                                contains($lkrmatch,' rencontres ') or
                                contains($lkrmatch,' school ') or
                                contains($lkrmatch,' schools ') or
                                contains($lkrmatch,' seminar ') or
                                contains($lkrmatch,' seminars ') or
                                contains($lkrmatch,' symp ') or
                                contains($lkrmatch,' symposium ') or
                                contains($lkrmatch,' symposiums ') or
                                contains($lkrmatch,' talk ') or
                                contains($lkrmatch,' talks ') or
                                contains($lkrmatch,' workshop ') or
                                contains($lkrmatch,' workshops ') ">

                  <datafield tag="980" ind1=" " ind2=" ">
                    <subfield code="a">ConferencePaper</subfield>
                  </datafield>
                </xsl:when>

              </xsl:choose>

              <xsl:if test="contains(./OAI-PMH:metadata/arXiv:arXiv/arXiv:categories, 'hep-')">
                <datafield tag="980" ind1=" " ind2=" ">
                  <subfield code="a">CORE</subfield>
                </datafield>
              </xsl:if>

              <datafield tag="541" ind1=" " ind2=" ">
                <subfield code="a">arxiv</subfield>
                <subfield code="c">OAI</subfield>
              </datafield>

              <datafield tag="980" ind1=" " ind2=" ">
                <subfield code="a">arXiv</subfield>
              </datafield>

              <datafield tag="980" ind1=" " ind2=" ">
                <subfield code="a">Citeable</subfield>
              </datafield>

              <datafield tag="980" ind1=" " ind2=" ">
                <subfield code="a">HEP</subfield>
              </datafield>

            </record>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:for-each>
    </collection>
  </xsl:template>
</xsl:stylesheet>
